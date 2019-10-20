# NBA-Chemistry

## Intro

I wanted to see if there is some way to quantify team chemistry. We can "feel" team chemistry improving or decaying, whether that is from hostile post-game interviews, trade rumors, toxic personalities joining/leaving the team. But how does this translate to actual play on the court, in a measurable way? That is what I want to explore using some "alternative" game stats.

## Methodology

First I needed to come up with some measure of team chemistry. This is hard to do with basic box score stats, and even some of the advanced ones like offensive/defensive rating can be affected by a poor shooting night rather than bad chemistry. Therefore, I turned to some more specialized stats from [stats.nba.com](https://stats.nba.com/teams/hustle/) that in my opinion, are more directly related to how well a team is playing together, or "chemistry".

I chose two stats that represent what I consider offensive and defensive chemistry, and these stats are as follows:

1. Screen Assists: The number of times an offensive player or team sets a screen for a teammate that directly leads to a made field goal by that teammate. A team that is playing well together will have great off ball movement, and set screens on or off ball setting up scores.
2. Secondary Assists:  A player is awarded a secondary assist if they passed the ball to a player who recorded an assist within 1 second and without dribbling. This shows how well the ball is hopping. Commentators always praise teams who are willing to make the extra pass, turning a good shot to a great shot.
3. Contested Shots: The number of times a defensive player or team closes out and raises a hand to contest a shot prior to its release. This stat shows how well the defense is moving together. More contested shots means the defense is not breaking down as often, most likely due to good chemistry and communication.
4. Deflections: The number of times a defensive player or team gets his hand on the ball on a non-shot attempt. A team who gets more deflections should be a team who's players are well positioned. Again, this should be due to playing well together defensively, and communicate well

I took the stats each team accumulated over every game, and with these four metrics, I did an equal weighting to create a single metric, which I call "Chemistry". Because each stat can vary in magnitude, I scaled each variable on a scale of 0-100 and take the average. I take a moving average of 8 games (~10% of the season) then I scale the Chemistry metric so that the starting value is always 100. So what we finally have is a measure of how a team's chemistry has changed relative to what they started at the beginning of the season, somewhat like a "Chemistry Index".

The resulting metric definitely has ups and downs, and it's not always super clear why. Could it be chemistry issues, or just some bad games vs. tougher opponents? Maybe. For now let's move on to the results and see if there is any information in there.

## Results

I plotted the Chemistry Index for all 30 teams. See the plots subdirectory for each team.

I was interested to see the results of a select few teams, ones that we already know had some chemistry issues. For every team I could think of, I added some points of interest where some potentially chemistry changing event happened (trade, coach firing, etc.). If you have any others to add, please let me know!

Here are a few examples I was excited to see:

### Houston Rockets

There are two main events that happened during this season: Carmelo being dismissed from the team after a terrible start, and then Chris Paul returning from injury after James Harden was carrying the team at MVP levels.

Carmelo's dismissal is pretty obvious. The team was performing very poorly, and Carmelo was not a good fit for this team. We can see here that shortly after Carmelo is dismissed, the Rockets' Chemistry Index notably improves.

After the season, we heard about Chris Paul and James Harden not getting along, and we were not too surprised when Paul got traded to OKC. Everyone within the Rockets denied there was any beef between the two, but the Chemistry Index shows a decline when CP3 returned from injury. Perhaps his and Harden's games just did not mesh well, and having two ball dominant players absoultely killed their offense.

### Los Angeles Lakers

The Lakers had a pretty disappointing season last year. They started off poorly, but looked to be picking it up, peaking at the Christmas Day game when LeBron went down with his injury. We can see here that the team started to suffer in chemistry shortly after LeBron went down (of course it would, it's fricking LeBron James).

The other interesting point of the season is at the end of January, when Anthony Davis informed the world he wanted out. The trade rumors started swirling, and everyone on the Lakers not named LeBron was avaialable and involved in trade talks. We can see here that the Chemistry Index plummeted during this time, and didn't recover until the trade deadline had passed (and LeBron returned from injury).

### GSW

The Warriors have some of the best chemistry in the league. However, the whole season was marred by Kevin Durant's coming free agency status. In fact, in early November, it culminated to a point where Draymond Green and Kevin Durant had a spat and had to be separated after a game. As can be seen, their Chemistry Index dropped quite a bit during this time though it did quickly recover.

### BOS

Last one I want to point out. We all know that Kyrie was an issue with the Celtics last year, and they had a very disappointing playoffs because of it. After some googling, the first instance I could find of the chemistry issues starting was on [January 9](https://www.boston.com/sports/boston-celtics/2019/06/28/jackie-macmullan-espn-kyrie-irving-brad-stevens), when Kyrie was reportedly upset that teammates went out to party in Miami the day before a game. As we can see, this is also around the time their Chemistry Index drops quickly.
