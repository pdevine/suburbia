import random
import events
import bubbles

phrases = '''
She'll love all this green when she gets home

Ooh I love the weekend

Next time I should remember to bring out some beers

It's looking good out here.  I should throw a BBQ.

If I get the edger out, it will look SO GOOD

Mine is easily the best on the block

This is great.  I haven't even thought about work.

It's so nice I could eat it.  Get me a big bowl of lawn salad!

No leaves!  Sweet!

It's like a zen garden, but better
'''
beginning = [phrase.strip() for phrase in phrases.split('\n') if phrase]

phrases = '''
Dana's over there with lemonade.  Textbook MILF.

If she shits on my lawn one more time...

Jim's kid is standing now

Dang my knee!  Should I get a riding mower?

When's the last time we all got together and grilled up some burgers?

A For Sale sign.  Hope the new people don't get too jealous over grass.

You can't even see the marks from that car crash anymore

If I owned that big one down the street, it wouldn't have brown patches like that

I could keep mine trimmed all the time too, if I was laid off
'''
foreshadowing = [phrase.strip() for phrase in phrases.split('\n') if phrase]
foreshadowing_themes = ['lust', 'anger', 'violence']


phrases = '''
Oh great, new guy has a huge dog.  We need to get that bylaw passed.

If I knew then what I know now, I would have fucked both of them

I think the only reason I'm going on business trips is the Asian stewardesses

Can't believe she'd complain about that ass.  Dana, girl, if you don't like it, you've got a neighbour willing to spank it for you.

Jim's kid, standing on his own.  Been in that chair all year.  Fucking Iraq.

I love her... but it's not like it was, like those first summers.

Which of my friends will be the first to die?

It's probably too late to do something that matters
'''
pain = [phrase.strip() for phrase in phrases.split('\n') if phrase]
pain_themes = ['anger', 'lust', 'lust', 'lust', 'violence']

phrases = '''
I could fake my death and move to Thailand and nobody would find me

She's got such low self-esteem, I wouldn't even have to try hard

If I dropped the mower over that little barking bitch would the organs and blood be like fertilizer?

I wish it was me that rolled over that IED.  I'd actually have a struggle that meant something.

Would I take an immortality pill if it meant watching everyone die?

I should have had the means to buy this whole street by now.  Instead I've got high cholesterol and Fido's shit on my shoe.

I wish I was drunk.  I should get a boat
'''
climax = [phrase.strip() for phrase in phrases.split('\n') if phrase]
climax_themes = ['violence', 'lust', 'anger', 'violence']

phrases = '''
I'm bored

I want more

I want something to happen

Why am I doing this?

I tried.  I tried really hard
'''
fin = [phrase.strip() for phrase in phrases.split('\n') if phrase]

gamePhases = [beginning, pain, climax, fin]

class StoryTeller(object):
    def __init__(self):
        events.AddListener(self)
        self.dayCounter = 0
        self.phaseIter = iter(gamePhases)
        self.phase = self.phaseIter.next()

    def On_Sunset(self):
        self.dayCounter += 1
        if self.phase == fin and self.phase:
            print 'new thought fin'
            events.Fire('NewThought', self.phase.pop(0))
            if len(self.phase) == 0:
                events.Fire('NarrativeOver')
                
        elif self.phase != fin:
            if self.dayCounter % 2 == 0:
                print 'new thought B'
                events.Fire('NewThought',
                            self.phase.pop(random.randint(0, len(self.phase))))
            if self.dayCounter % 4 == 0:
                self.phase = self.phaseIter.next()
        
