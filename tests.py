# -*- coding: utf8 -*-
import datetime
from django.utils import unittest
from django.utils.timezone import now
from bolti.models import Player, Match, Squad, ScoreBoard, Practice

class TestMatches(unittest.TestCase):
    def setUp(self):
        #Ætlum að búa til töflu með sex leikmönnum þ.a. stöðutaflan sé unambiguous
        """
            1   9  8-2=6
            2   6  7-2=4
            3   6  5-5=0
            4   3  0-2+4-1+1-2=0
            5   3  -2-3+1=-4
            6   0  -6

            123 vs. 456
            2 - 0

            124 vs. 356
            4 - 1

            135 vs. 246
            2 - 1
        """
        Player.objects.all().delete(); Match.objects.all().delete(); ScoreBoard.objects.all().delete()
        names_emails = [('Player %s'%str(v+1), 'example%d@example.org'%(v+1)) for v in range(6)]
        players = [Player.objects.create(name = name, email = email) for name, email in names_emails]
        p = Practice.objects.create(dt=now()+datetime.timedelta(hours=3))
        p.players = players
        home = Squad.objects.create()
        home.players=players[:3]
        away = Squad.objects.create()
        away.players=players[-3:]
        Match.objects.create(score=(2,0), 
                                home=home, 
                                away=away,
                                practice=p
                            )
        home = Squad.objects.create()
        home.players=[players[0], players[1], players[3]]
        away = Squad.objects.create()
        away.players=[players[2], players[4], players[5]]
        Match.objects.create(score=(4,1), 
                                home=home, 
                                away=away,
                                practice=p
                            )
        home = Squad.objects.create()
        home.players=[players[1], players[3], players[5]]
        away = Squad.objects.create()
        away.players=[players[0], players[2], players[4]]
        Match.objects.create(score=(1,2), 
                                away=away, 
                                home=home,
                                practice=p
                            )
                            
    def test_check_next_match_squads_are_fair(self):
        practice = Practice.objects.get(dt__range=(now()-datetime.timedelta(hours=12), 
                    now()+datetime.timedelta(hours=12)))
        home, away = practice.teams_idea()
        homepoints_sum = sum([player.scoreboard_statusline.points for player in home])
        awaypoints_sum = sum([player.scoreboard_statusline.points for player in away])
        self.assertEqual(homepoints_sum, 18)
        self.assertEqual(awaypoints_sum, 9)
        
    def test_check_order_is_right(self):
        sb = ScoreBoard.objects.order_by('-created')[0]
        lines = sb.ordered()
        nums = [int(line.player.name[-1]) for line in lines]
        for i in range(6):
            self.assertEqual(i+1, nums[i])
            
    def test_check_scores(self):
        scores = [match.score for match in Match.objects.all()]
        self.assertTrue((2,0) in scores and (4,1) in scores and (1,2) in scores)

