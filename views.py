import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import now
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from bolti.models import Practice, Player, Registration, Match, Squad

def main(request):
    practices = Practice.objects.filter(dt__range=(now()-datetime.timedelta(days=1), 
                now()+datetime.timedelta(days=2)))
    for practice in practices:
        practice.form = RegisterForm(initial={'practice': practice})
    return render_to_response('main.html', {'practices': practices}, context_instance=RequestContext(request))
    
def register(request, practiceid):
    form = RegisterForm(request.REQUEST)
    data = {}
    if form.is_valid():
        practice = Practice.objects.get(pk=practiceid)
        Registration.objects.get_or_create(player=form.cleaned_data['player'], practice=practice)
        data['playername'] = form.cleaned_data['player'].name
    else:
        data['form'] = NewPlayerForm(initial={'name': request.REQUEST['player']}).as_p()
        data['formurl'] = reverse(newplayer, args=(practiceid, ))
    data['res'] = form.is_valid()
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    
def remove(request, practiceid):
    form = RemoveForm(request.REQUEST)
    if form.is_valid():
        practice = Practice.objects.get(pk=practiceid)
        Registration.objects.filter(practice=practice, player=form.cleaned_data['player']).delete()
    return HttpResponse(simplejson.dumps(form.is_valid()), mimetype='application/json')
        
    
def newplayer(request, practiceid):
    form = NewPlayerForm(request.REQUEST)
    if form.is_valid():
        form.save()
        practice = Practice.objects.get(pk=practiceid)
        Registration.objects.get_or_create(player=form.instance, practice=practice)
        return HttpResponse(simplejson.dumps({'res': True}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'res': False, 'errors': form.errors}), mimetype='application/json')
    
@csrf_exempt
def register_scores(request, practiceid):
    if request.method == 'POST':
        try:
            homeplayers = 'hometeam[]' in request.POST and request.POST.getlist('hometeam[]') or request.POST.getlist('hometeam')
            awayplayers = 'awayteam[]' in request.POST and request.POST.getlist('awayteam[]') or request.POST.getlist('awayteam')
            score = tuple([int(request.POST['homescore']), int(request.POST['awayscore'])])
        except KeyError:
            return HttpResponse(simplejson.dumps({'res': False}), mimetype='application/json')
        homeplayers = Player.objects.filter(name__in=homeplayers).order_by('name')
        awayplayers = Player.objects.filter(name__in=awayplayers).order_by('name')
        
        home, created = Squad.objects.get_or_create(identifier='-'.join([p.name for p in homeplayers.order_by('name')]))
        if created:
            home.players = homeplayers
            home.create_identifier()
        away, created = Squad.objects.get_or_create(identifier='-'.join([p.name for p in awayplayers.order_by('name')]))
        if created:
            away.players = awayplayers
            away.create_identifier()
        match = Match.objects.create(practice=Practice.objects.get(pk=practiceid), 
                                    score=score,
                                    home=home,
                                    away=away)
        return HttpResponse(simplejson.dumps({'res': True}), mimetype='application/json')
    else:    
        home, away = Practice.objects.get(pk=practiceid).teams_idea(names=True)
        return HttpResponse(simplejson.dumps({'home': home, 'away': away}), mimetype='application/json')
    
def autocomplete(request):
    if not request.GET.get('term'):
        return HttpResponse(simplejson.dumps([]), mimetype='application/json')

    q = request.GET.get('term')

    players = Player.objects.filter(name__istartswith=q)
    return HttpResponse(simplejson.dumps([player.name for player in players]), mimetype='application/json')
    
#Bug: Forms can't be imported before autocomplete as RegisterForm uses reverse for autocomplete
from bolti.forms import RegisterForm, NewPlayerForm, RemoveForm, RegisterScoresForm