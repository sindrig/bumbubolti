from collections import defaultdict
from django.db import models
from django.db.models.signals import post_save
from django.utils.formats import date_format
from django.utils.timezone import now
from django.forms.widgets import flatatt
from bolti.fields import ScoreField
from django.utils.translation import ugettext as _
# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length = 100, unique=True)
    email = models.EmailField(unique=True)
    
    @property
    def scoreboard_statusline(self):
        if self.statusline.exists():
            return self.statusline.order_by('-scoreboard__created')[0]
        return ScoreBoardStatusLine(player=self)
    
class Squad(models.Model):
    identifier = models.TextField(blank=True, default='')
    players = models.ManyToManyField(Player, related_name='squads')
    
    def create_identifier(self):
        self.identifier = '-'.join([p.name for p in self.players.order_by('name')])    
        self.save()
    
class Practice(models.Model):
    players = models.ManyToManyField(Player, blank=True, through='Registration')
    dt = models.DateTimeField()

    class Meta:
        ordering = ['-dt']

    def __unicode__(self):
        return date_format(self.dt, 'DATE_FORMAT') + ' - ' + date_format(self.dt, 'TIME_FORMAT')
        
    @property
    def has_started(self):
        return self.dt < now()

    def teams_idea(self, names=False):
        def inner():
            try:
                sb = ScoreBoard.objects.order_by('-created')[0]
            except IndexError:
                p = self.players.order_by('?')
                return p[len(p)/2:], p[:len(p)/2]
            playing = self.players.all()
            ordered = [line.player for line in sb.ordered() if line.player in playing]
            return ordered[::2], ordered[1::2]
        if not names: return inner()
        return [[player.name for player in team] for team in inner()]
        
        
class Registration(models.Model):
    player = models.ForeignKey(Player)
    practice = models.ForeignKey(Practice)
    registered = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['registered']
        
class Match(models.Model):
    score = ScoreField(default=(0,0))
    practice = models.ForeignKey(Practice)
    home = models.ForeignKey(Squad, related_name='homegames')
    away = models.ForeignKey(Squad, related_name='awaygames')
    
class ScoreBoard(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    _prepared = 0
    
    def prepare(self, order_by = ['-points_per_match', '-points', '-scored', 'conceded']):
        self._lines = self.lines.select_related('player').order_by(*order_by)
        self._prepared = 1
        
    def ordered(self, order_by = ['-points_per_match', '-points', '-scored', 'conceded']):
        if not hasattr(self, '_lines'):
            self._lines = self.lines.select_related('player').order_by(*order_by)
        return self._lines.order_by(*order_by)
        
    def p(self):
        #Prints scoreboard to standard output
        if not self._prepared:
            self.prepare()
        print '\t'.join(['Pos', 'Name', 'Played', 'Scored', 'Conceded', 'Net', 'Points'])
        for i, line in enumerate(self._lines):
            print '%d\t%s'%(i, line)
            
    def as_table(self, table_attrs={'class': 'scoreboard'}):
        if not self._prepared:
            self.prepare()
        table_attrs = flatatt(table_attrs)
        buf = ['<table %s'%table_attrs]
        buf.append(u'<tr><th>%s</th></tr>'%u'</th><th>'.join([_('Pos'), 
            _('Name'), _('Played'), _('Scored'), _('Conceded'), _('Net'), 
            _('Points'), _('Points per match')]))
        for i, line in enumerate(self._lines):
            buf.append(u'<tr><td>%s</td></tr>'%u'</td><td>'.join([str(i+1)]+line.as_list()))
        buf.append('</table>')
        return u''.join(buf)
        
    
class ScoreBoardStatusLine(models.Model):
    player = models.ForeignKey(Player, related_name='statusline')
    played = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    scored = models.IntegerField(default=0)
    conceded = models.IntegerField(default=0)
    points_per_match = models.FloatField(default=0.0)
    scoreboard = models.ForeignKey(ScoreBoard, related_name='lines')
    
    def __unicode__(self):
        return '\t'.join([self.player.name, str(self.played), str(self.scored), 
            str(self.conceded), str(self.net), str(self.points), str(self.points_per_match)])
        
    def as_list(self):
        return [self.player.name, str(self.played), str(self.scored), 
            str(self.conceded), str(self.net), str(self.points), str(self.points_per_match)]
        
    def save(self, *args, **kwargs):
        self.points_per_match = float(self.points)/float(self.played)
        super(ScoreBoardStatusLine, self).save(*args, **kwargs)
    
    @property
    def net(self):
        return self.scored-self.conceded
        
        
        
def update_scoreboard(sender, instance, created, **kwargs):
    sb = ScoreBoard.objects.create()
    sbsls = defaultdict(ScoreBoardStatusLine)
    for match in Match.objects.all():
        hp = match.home.players.all()
        ap = match.away.players.all()
        if match.score[0] > match.score[1]: #Home team won
            for player in hp:
                sbsls[player.id].points += 3
        elif match.score[0] < match.score[1]: #Away team won
            for player in ap:
                sbsls[player.id].points += 3
        else: #Draw
            for player in list(ap)+list(hp):
                sbsls[player.id].points += 1
        #G/D
        for player in hp:
            sbsls[player.id].scored += match.score[0]
            sbsls[player.id].conceded += match.score[1]
        for player in ap:
            sbsls[player.id].scored += match.score[1]
            sbsls[player.id].conceded += match.score[0]
        #Played
        for player in list(hp)+list(ap):
            sbsls[player.id].played += 1
    for playerid, sbsl in sbsls.items():
        sbsl.player_id = playerid
        sbsl.scoreboard = sb
        sbsl.save()
        
post_save.connect(update_scoreboard, sender=Match)
        
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^bolti\.fields\.ScoreField"])
except ImportError:
    pass
