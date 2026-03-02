# Is the Pistons lack of shooting a problem in the playoffs?  

Data via Cleaning the Glass  

The 2025-2026 Pistons will likely be the Eastern Conference’s 1 seed after, for the most part, successfully navigating a tougher stretch of schedule in February. We are officially thinking about multiple rounds of playoffs with the following roster:  

<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/Pistons%20Roster.png" alt="Pistons Roster">  

I’ll dive further into some on/off diff numbers within this repo. In particular, I will use these differentials and other per 100 possessions differentials to really study Ausar Thompson and the Pistons lack of outside shooting as they look to finish the season and hopefully make a deep playoff run.  

Of course, on/off differentials and lineups are not everything. I’m not here to tell you that because Duncan Robinson has a 5.3 on/off diff that he is a better basketball player than Ausar Thompson’s 3.4 on/off diff. I am here to tell you that Ausar can play in some clunky lineups that impacts his overall differential negatively.  

## Do non-shooting teams excel in the postseason?  

Less narrative here now. Pointing to most of my code and the below visuals. More or less, the conclusion is that our ceiling is the early 2020s Miami Heat. Meaning we can make the finals but will probably be heavy underdogs if we got there. This is based on the below visual conclusions as well as perception and observations from myself and other pundits (i.e. Zach Lowe).  

<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/playoff_lineups_low_3pa.png" alt="Low Freq 3 Lineups">

<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/low_accuracy_lineups_visual.png" alt="Low Accuracy 3 Lineups">  

## Should Ausar Thompson play more minutes?  

It’s weird that Ausar Thompson plays 26 minutes on the Pistons and his twin brother is second in the league in MPG at 37 minutes. They are virtually the same player in terms of build, skillset, plus offensive and defensive acumen. Their effective FG% are 0.1 percentage points off of each other’s. Even if you say that Amen handles the ball more this year without Fred Van Vleet, you can point to last year where Amen played 32 minutes a game.  


## Need to clean a bit of the below:  

Feb 23 Note 1: Ausar played 19 minutes against the Spurs tonight... why  
Feb 23 Note 2: Playing around with Cursor to find the lineups with low frequency three point shooters. Main visual below. Need to cleanup and add context.  
Feb 25 Note: Tinkering with some lineup stuff. Sasser not playing more? Levert... bruh. Why does Ausar seem to be so bad in transition offense? For example, Ausar is obviously a defensive demon, but the Pistons score better in transition by 0.4 points with him off than on. Amen is +1.2 off steals, for reference.  
Other Notes: Zach Lowe exploring Pistons parallels to recent teams. Notably, the 2022 Memphis Grizzlies with defense-first team with an all-NBA young PG. He also mentioned challenges in teams with limited playoff exposure being successful in the postseason, which I generally disagree with. Early Warriors and Cavs (Lebron aside) had very limited postseason experience. Within this, he mentioned the 2020 Heat as a team with similar lack of postseason experience. The defense-first and multiple non 3-point shooters on the floor serve as a good parallel.  


 

## Early Notes  
I'm really puzzled by Ausar Thompson being a high-minutes (30+) on a successful playoff team.  

-He plays limited minutes now; 6th on the team in minutes per game. Fully understand that teams are distributing more minutes now tham ever before. But this gets tighter in the playoffs (data to support?)  
-He cannot shoot whatsoever. So, I wonder what his role is during the fourth quarter of a playoff game.  
-There has been interesting plus/minus numbers in early Jan 2025 games plus further questionable on/off stats. Will look to confirm/debunk these a bit.  

Beyond Ausar's limitations, Ron Holland and Jaden Ivey are quite duplicative as young wings, primarily Ron Holland as a defense-first wing.

Notes 2/21 - How does this change with Jaden Ivey getting traded? Could this lead to more minutes for Ausar + Ron? What do the numbers look like with Ausar and Ron on the floor together?

Other Notes - Need more data and visuals. Get to a predictive analysis on minutes expectation in the playoffs...

## Why does Ausar Thompson play so few minutes per game?  

### General Minutes per Game Reductions over Time  

Questions to Answer:  
Why is Ausar Thompson playing less minutes per game than my own expectations?  
-Amen is playing the second most minutes in the league, for reference.  
Are players generally playing less minutes per game than usual?  
-If so, why? Could it be contributed to a higher variance in game margins? Could you look at minutes played in only the first three quarters of a game?  
-Probably team by team and may or may not change in the playoffs.  
He also commits a lot of fouls compared to others at his position.  

Quick Blurb: Get to a good graph of minute trends  
Ausar’s minutes follow the general trend of starters and high-minutes players playing less minutes per game, but that is consistent across the type of player you are (I.e. Superstar, Starter, Role Player). If anything, more players are playing small amounts of minutes. For example, in the Pistons most recent 15-point win over the Knicks, the Pistons played 10 players. Every player played over 12 minutes and nine of ten players logged 18 or more minutes. This could also be consistent with JB Bickerstaff’s coaching style. Even reaching back to a February 2019 game when he was the coach of the Memphis Grizzlies, 9 players logged over 10 minutes in their close game over the LA Clippers. Of course, there are coaches who still ride players long like Tom Thibodeau. In this recent example of the Knicks-Pistons, 9 players played 10 or more minutes. Last year, a big February game against the Celtics saw 8 players play 10 or more minutes.  

### Ausar Thompson vs Ron Holland  
A potential deterrent to more minutes for Thompson is that the Pistons also want to continue to develop second year player Ron Holland who profiles very similar to Ausar.  

Offensive Comparison  
Below we have a couple of absolute brick layers on offense.  

Ausar  
<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/Ausar%20Offense.png" alt="Ausar Offensive Stats">

Ron  
<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/Ron%20Offense.png" alt="Ron Offensive Stats">

Defensive Comparison  
Absolute honey badgers on the defensive end. If I caught the ball in a matchup with either of them I would hot potato it right back to who passed it to me. It would still probably be a turnover.  

Ausar  
<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/Ausar%20Defense.png" alt="Ausar Defensive Stats">

Ron  
<img src="https://github.com/TenoBall/Pistons-Advanced-Stats/blob/main/Ron%20Defense.png" alt="Ron Defensive Stats">

###Other Early Notes  

Pistons Lineups  
Questions to Answer:  
Can the Pistons play two non-shooter wings with Cade effectively in the playoffs?  
What about Duren-Ausar lineups?  
Reminds me of some Josh Hart-Mitchell Robinson lineups. Could also look into some lineups from the Pistons playoff series last year. Amen’s other series as well. All of these lineups were really bad shooting.  
Are there similar lineups in recent postseasons that have yielded success?  
Can base this on 3PT attempts numbers.  
Predictive Model  
At some point, how can I add a predictive model to this work?  

Predictive expectation with minutes played in the playoffs with Pistons lineups?  
