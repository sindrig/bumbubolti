from collections import defaultdict
from django.db import models
from django.db.models.signals import post_save
from bolti.fields import ScoreField
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
    players = models.ManyToManyField(Player, related_name='squads')
    
class Practice(models.Model):
    players = models.ManyToManyField(Player)
    dt = models.DateTimeField()

    def teams_idea(self):
        try:
            sb = ScoreBoard.objects.order_by('-created')[0]
        except IndexError:
            p = self.players.order_by('?')
            return p[len(p)/2:], p[:len(p)/2]
        playing = self.players.all()
        ordered = [line.player for line in sb.ordered() if line.player in playing]
        return ordered[::2], ordered[1::2]
        
class Match(models.Model):
    score = ScoreField(default=(0,0))
    practice = models.ForeignKey(Practice)
    home = models.ForeignKey(Squad, related_name='homegames')
    away = models.ForeignKey(Squad, related_name='awaygames')
    
class ScoreBoard(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    _prepared = 0
    
    def prepare(self, order_by = '-points'):
        self._lines = self.lines.select_related('player').order_by(order_by)
        self._prepared = 1
        
    def ordered(self, order_by = '-points'):
        if not hasattr(self, '_lines'):
            self._lines = self.lines.select_related('player').order_by(order_by)
        return self._lines.order_by(order_by)
        
    def p(self):
        #Prints scoreboard to standard output
        if not self._prepared:
            self.prepare()
        print '\t'.join(['Pos', 'Name', 'Played', 'Scored', 'Conceded', 'Net', 'Points'])
        for i, line in enumerate(self._lines):
            print '%d\t%s'%(i, line)
    
class ScoreBoardStatusLine(models.Model):
    player = models.ForeignKey(Player, related_name='statusline')
    played = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    scored = models.IntegerField(default=0)
    conceded = models.IntegerField(default=0)
    scoreboard = models.ForeignKey(ScoreBoard, related_name='lines')
    
    def __unicode__(self):
        return '\t'.join([self.player.name, str(self.played), str(self.scored), str(self.conceded), str(self.net), str(self.points)])
    
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
        
