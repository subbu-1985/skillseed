"""
Seed all 210 MCQs into the correct skillset modules.
Each skill has 3 modules. Each module gets 10 questions, 4 options each.
Each Knowledge Check samples 3 random questions from the pool of 10.
Run: python seed_mcq.py
"""
import asyncio
import uuid
from sqlalchemy import select, delete
from app.database import AsyncSessionLocal, engine
from app.models.skill import Skill, SkillModule
from app.models.quiz import Quiz, QuizQuestion, QuizOption

# ─────────────────────────────────────────────────────────────
# MCQ BANK: skill_name -> [module1_questions, module2_questions, module3_questions]
# Each question: {"q": "...", "opts": ["A","B","C","D"], "correct": 0}  (correct = index)
# ─────────────────────────────────────────────────────────────
MCQ_BANK = {
    "Communication": [
        # Module 1 — Communication Basics
        [
            {"q": "What is the primary purpose of communication?", "opts": ["To win arguments", "To share information and understanding between people", "To impress others with vocabulary", "To fill silence"], "correct": 1},
            {"q": "Which of the following is an example of non-verbal communication?", "opts": ["Writing an email", "Making a phone call", "Making eye contact while speaking", "Sending a text message"], "correct": 2},
            {"q": "Active listening means:", "opts": ["Talking more than the other person", "Waiting for your turn to speak", "Fully concentrating on and understanding what the speaker is saying", "Nodding without paying attention"], "correct": 2},
            {"q": "Which tone is most appropriate when speaking to a teacher?", "opts": ["Casual and informal", "Loud and assertive", "Respectful and clear", "Sarcastic and joking"], "correct": 2},
            {"q": "What does 'body language' refer to?", "opts": ["The words you choose to speak", "Physical movements and gestures that communicate feelings", "The speed at which you talk", "The volume of your voice"], "correct": 1},
            {"q": "A good communicator should:", "opts": ["Interrupt to show they are engaged", "Take turns speaking and listening", "Always agree with the other person", "Speak only when spoken to"], "correct": 1},
            {"q": "Which is a barrier to effective communication?", "opts": ["Clear language", "Good eye contact", "Distractions like checking your phone", "Asking clarifying questions"], "correct": 2},
            {"q": "When you paraphrase someone, you are:", "opts": ["Repeating their words exactly", "Restating their message in your own words to confirm understanding", "Disagreeing with them politely", "Summarising your own thoughts"], "correct": 1},
            {"q": "Which of these is an example of verbal communication?", "opts": ["A thumbs-up gesture", "A smile", "A spoken presentation to the class", "A handshake"], "correct": 2},
            {"q": "Why is eye contact important during a conversation?", "opts": ["It makes the other person uncomfortable", "It shows you are trying to dominate", "It shows you are attentive and engaged", "It is not important at all"], "correct": 2},
        ],
        # Module 2 — Advanced Communication 2
        [
            {"q": "Assertive communication means:", "opts": ["Demanding your way at all times", "Staying silent to avoid conflict", "Expressing your needs clearly and respectfully", "Agreeing with everything said"], "correct": 2},
            {"q": "Which communication style tends to build the healthiest relationships?", "opts": ["Passive", "Aggressive", "Passive-aggressive", "Assertive"], "correct": 3},
            {"q": "Empathy in communication involves:", "opts": ["Feeling sorry for someone", "Understanding and sharing the feelings of another person", "Agreeing with everything they say", "Offering solutions immediately"], "correct": 1},
            {"q": "Constructive feedback should be:", "opts": ["Personal and critical", "Vague and general", "Specific, respectful, and focused on behaviour, not the person", "Only positive, never negative"], "correct": 2},
            {"q": "What is the 'sandwich method' of feedback?", "opts": ["Giving feedback only during lunch", "Placing constructive criticism between two pieces of positive feedback", "Giving three criticisms in a row", "Avoiding negative feedback entirely"], "correct": 1},
            {"q": "Which of the following best describes two-way communication?", "opts": ["One person talks; the other listens silently", "Communication via email only", "Both parties send and receive messages in exchange", "A broadcast message to many people"], "correct": 2},
            {"q": "When adapting your communication style to your audience, you should consider:", "opts": ["Only your own comfort", "The most complex vocabulary you know", "Their age, knowledge level, and relationship to you", "How quickly you can finish the conversation"], "correct": 2},
            {"q": "In a debate, the most effective strategy is to:", "opts": ["Speak the loudest", "Repeat your point over and over", "Use evidence and logical reasoning to support your argument", "Dismiss the other person's views immediately"], "correct": 2},
            {"q": "Which is an example of open-ended questioning?", "opts": ["Did you like it?", "Was that good?", "Is this right?", "What did you think about that experience?"], "correct": 3},
            {"q": "'Reading the room' means:", "opts": ["Silently reading a book in public", "Sensing the mood and emotional atmosphere of a group", "Memorising a speech before delivering it", "Making eye contact with everyone individually"], "correct": 1},
        ],
        # Module 3 — Advanced Communication 3
        [
            {"q": "Persuasive communication relies heavily on:", "opts": ["Repetition and volume", "Credibility, emotional appeal, and logical reasoning", "Complicated language", "Avoiding questions from the audience"], "correct": 1},
            {"q": "Which of the following is a sign of an ineffective public speaker?", "opts": ["Using pauses deliberately", "Reading directly from notes without looking up", "Varying their tone and pitch", "Making their key point early"], "correct": 1},
            {"q": "Cross-cultural communication requires:", "opts": ["Assuming everyone shares the same customs", "Awareness and respect for cultural differences in expression", "Speaking in a single universal language only", "Ignoring cultural context"], "correct": 1},
            {"q": "What is 'active silence' in communication?", "opts": ["Refusing to participate in a conversation", "Deliberately pausing to allow the other person to reflect or respond", "Daydreaming during a conversation", "Waiting impatiently for your turn"], "correct": 1},
            {"q": "A 'call to action' in communication is:", "opts": ["A request to make a phone call", "An emergency announcement", "A clear statement that prompts the audience to do something specific", "A summary of what was already said"], "correct": 2},
            {"q": "Which skill is most critical when resolving a miscommunication?", "opts": ["Being louder than the other person", "Clarifying intent and actively listening without assumptions", "Proving the other person wrong", "Avoiding the topic entirely"], "correct": 1},
            {"q": "Diplomatic communication means:", "opts": ["Speaking only in formal settings", "Using technical government language", "Delivering difficult messages honestly but with sensitivity and tact", "Avoiding all conflict at any cost"], "correct": 2},
            {"q": "When giving a presentation, which technique best maintains audience engagement?", "opts": ["Speaking in a monotone voice for consistency", "Avoiding questions at the end", "Incorporating stories, questions, and visual aids", "Reading slides word for word"], "correct": 2},
            {"q": "Non-violent communication (NVC) focuses on:", "opts": ["Never expressing disagreement", "Expressing feelings and needs without blame or judgment", "Winning every argument peacefully", "Avoiding all emotional topics"], "correct": 1},
            {"q": "The most important element of a strong conclusion in a speech is:", "opts": ["Introducing a new, unrelated topic", "Apologising for the length of the speech", "Reinforcing the core message and leaving the audience with a lasting thought", "Listing all the points made in detail"], "correct": 2},
        ],
    ],
    "Leadership": [
        [
            {"q": "Leadership is best defined as:", "opts": ["Telling people what to do", "Being the loudest in the room", "Guiding and inspiring others towards a shared goal", "Having a title or position of authority"], "correct": 2},
            {"q": "Which quality is most important in a good leader?", "opts": ["Perfectionism", "Trustworthiness and integrity", "The ability to work alone", "Being the most intelligent person"], "correct": 1},
            {"q": "A role model leader:", "opts": ["Only leads when things are easy", "Takes credit for others' work", "Demonstrates the behaviour they expect from others", "Avoids making decisions"], "correct": 2},
            {"q": "The difference between a boss and a leader is:", "opts": ["A boss earns more money", "A leader empowers others, while a boss controls them", "A leader only exists in corporations", "There is no difference"], "correct": 1},
            {"q": "Which of the following shows initiative?", "opts": ["Waiting for someone else to identify a problem", "Identifying a problem and proposing a solution without being asked", "Following instructions perfectly", "Completing work at the last minute"], "correct": 1},
            {"q": "Why is self-awareness important for a leader?", "opts": ["It makes leaders appear more intelligent", "It helps leaders understand their strengths, weaknesses, and impact on others", "It allows leaders to avoid criticism", "It is not important for leadership"], "correct": 1},
            {"q": "A student leader organising a group project should do what first?", "opts": ["Assign all work to the most capable student", "Start working immediately without planning", "Discuss everyone's strengths and delegate accordingly", "Complete all the work themselves"], "correct": 2},
            {"q": "Good leaders handle mistakes by:", "opts": ["Blaming team members", "Hiding the mistake", "Owning responsibility and learning from what went wrong", "Pretendining it never happened"], "correct": 2},
            {"q": "Which of these is a sign of poor leadership?", "opts": ["Listening to the team's concerns", "Micromanaging every detail and not trusting the team", "Giving clear instructions", "Celebrating team success"], "correct": 1},
            {"q": "Motivation in leadership refers to:", "opts": ["Forcing people to work harder", "Inspiring others to give their best effort willingly", "Offering only financial rewards", "Ignoring team morale"], "correct": 1},
        ],
        [
            {"q": "Transformational leadership focuses on:", "opts": ["Maintaining the status quo", "Using rewards to control behaviour", "Inspiring change and growth in individuals and organisations", "Micromanaging daily tasks"], "correct": 2},
            {"q": "Which leadership style is most effective during a crisis?", "opts": ["Laissez-faire (hands-off)", "Decisive and directive leadership to provide clear direction quickly", "Democratic leadership with lengthy group votes", "No particular style is needed"], "correct": 1},
            {"q": "Emotional intelligence (EQ) in a leader includes:", "opts": ["Having a high IQ", "Suppressing emotions at all times", "Recognising, understanding, and managing one's own and others' emotions", "Avoiding emotional conversations entirely"], "correct": 2},
            {"q": "Delegating effectively means:", "opts": ["Giving someone a task and ignoring them", "Assigning the right task to the right person with clear expectations", "Doing the task yourself to save time", "Dividing tasks randomly"], "correct": 1},
            {"q": "How should a leader handle a conflict between two team members?", "opts": ["Take sides with the more experienced member", "Ignore it and hope it resolves itself", "Facilitate a calm, structured conversation to find a fair resolution", "Remove one person from the team immediately"], "correct": 2},
            {"q": "A vision statement in leadership is important because it:", "opts": ["Lists the rules every team member must follow", "Provides a clear, inspiring picture of the future the team is working toward", "Describes the leader's personal goals", "Outlines the team's budget"], "correct": 1},
            {"q": "Servant leadership is characterised by:", "opts": ["The leader always making decisions alone", "Putting the leader's needs first", "Prioritising the growth and well-being of team members above personal gain", "Demanding loyalty from followers"], "correct": 2},
            {"q": "Which is an example of leading by example?", "opts": ["Telling the team to be punctual while arriving late yourself", "Being the first to arrive and last to leave during a critical project", "Delegating all difficult tasks to others", "Setting rules that apply to others but not yourself"], "correct": 1},
            {"q": "Accountability in leadership means:", "opts": ["Punishing the team when goals are not met", "Taking responsibility for both successes and failures", "Reporting only positive progress", "Shifting blame to external factors"], "correct": 1},
            {"q": "'Coaching' as a leadership approach involves:", "opts": ["Training athletes for sport", "Asking questions and guiding individuals to discover their own solutions", "Providing all the answers to the team", "Only praising performance, never critiquing it"], "correct": 1},
        ],
        [
            {"q": "Strategic thinking in leadership means:", "opts": ["Reacting to problems as they arise", "Planning long-term goals while anticipating challenges and opportunities", "Focusing only on immediate tasks", "Delegating all planning to others"], "correct": 1},
            {"q": "Which best describes an inclusive leader?", "opts": ["One who favours the highest performers", "One who ensures every team member feels valued, heard, and involved", "One who makes all decisions independently", "One who avoids difficult conversations"], "correct": 1},
            {"q": "When navigating organisational change, a leader should:", "opts": ["Make all changes secretly to avoid resistance", "Communicate transparently, address concerns, and build buy-in", "Force the team to accept change without discussion", "Wait until everyone agrees before making any changes"], "correct": 1},
            {"q": "Ethical leadership means:", "opts": ["Following only the rules that benefit you", "Making decisions based on fairness, honesty, and respect for all stakeholders", "Prioritising profits above all else", "Avoiding any controversial decision"], "correct": 1},
            {"q": "A leader's legacy is best defined as:", "opts": ["The salary they earned", "The number of titles they held", "The lasting positive impact they had on people and the organisation", "The length of time they held a position"], "correct": 2},
            {"q": "Distributed leadership refers to:", "opts": ["Spreading a leader's workload to reduce stress", "Sharing leadership responsibilities across multiple team members based on expertise", "Having several people with the same job title", "Rotating the leader role randomly"], "correct": 1},
            {"q": "In high-stakes decision-making, a leader should:", "opts": ["Always trust their gut instinct alone", "Gather relevant data, consult stakeholders, and weigh risks before deciding", "Make the quickest decision possible", "Defer all decisions to a higher authority"], "correct": 1},
            {"q": "What is 'psychological safety' in a team environment?", "opts": ["Ensuring the workplace is physically safe", "Providing mental health counselling to all team members", "Creating an environment where people feel safe to speak up and make mistakes without fear", "Limiting the team's workload to reduce stress"], "correct": 2},
            {"q": "Mentoring future leaders primarily involves:", "opts": ["Completing their work for them", "Sharing experience, providing guidance, and creating growth opportunities", "Monitoring their every action", "Only intervening when they make mistakes"], "correct": 1},
            {"q": "Which is the most accurate description of adaptive leadership?", "opts": ["Changing your personality to suit every situation", "Adjusting your leadership approach to meet the unique demands of different challenges", "Never committing to one leadership style", "Only leading when circumstances are familiar"], "correct": 1},
        ],
    ],
    "Time Management": [
        [
            {"q": "Time management is best described as:", "opts": ["Working as fast as possible", "Planning and organising how to divide your time between tasks effectively", "Doing more tasks at the same time", "Avoiding all breaks during study"], "correct": 1},
            {"q": "Which tool is most commonly used to plan and schedule tasks?", "opts": ["A mirror", "A planner or calendar", "A stopwatch", "A calculator"], "correct": 1},
            {"q": "Procrastination means:", "opts": ["Completing tasks ahead of schedule", "Working on multiple tasks simultaneously", "Delaying or postponing tasks unnecessarily", "Prioritising urgent tasks first"], "correct": 2},
            {"q": "Which of the following is the best way to start managing your time better?", "opts": ["Stay up late to finish everything", "Write a to-do list and prioritise tasks", "Only do tasks you enjoy", "Avoid planning and work spontaneously"], "correct": 1},
            {"q": "A 'deadline' is:", "opts": ["The time you wake up each morning", "A task you have completed", "The latest time or date by which a task must be finished", "A break between study sessions"], "correct": 2},
            {"q": "What does 'prioritising' tasks mean?", "opts": ["Doing the easiest tasks first", "Doing all tasks at the same speed", "Deciding which tasks are most important and doing them first", "Avoiding difficult tasks until last"], "correct": 2},
            {"q": "Which habit best helps students avoid forgetting assignments?", "opts": ["Relying on memory alone", "Writing down tasks and deadlines as soon as they are given", "Checking social media for reminders", "Asking friends what is due"], "correct": 1},
            {"q": "Breaks during study are important because:", "opts": ["They help you avoid all your work", "They allow your brain to rest and maintain focus over longer periods", "They make study sessions shorter", "They are only for younger students"], "correct": 1},
            {"q": "Which of the following is NOT a time waster?", "opts": ["Scrolling social media during study", "Reviewing your to-do list at the start of each day", "Spending too long on unimportant tasks", "Attending unnecessary meetings"], "correct": 1},
            {"q": "Setting goals helps with time management because:", "opts": ["It reduces the amount of work you have to do", "It gives you a clear direction and helps you focus your time and energy", "It allows you to ignore low-priority tasks permanently", "It guarantees you will always finish on time"], "correct": 1},
        ],
        [
            {"q": "The Eisenhower Matrix categorises tasks by:", "opts": ["Difficulty and length", "Subject and topic", "Urgency and importance", "Cost and benefit"], "correct": 2},
            {"q": "A task that is 'urgent but not important' should ideally be:", "opts": ["Done immediately by you", "Delegated to someone else if possible", "Ignored entirely", "Added to a long-term goal list"], "correct": 1},
            {"q": "The Pomodoro Technique involves:", "opts": ["Studying for 2 hours without stopping", "Working for 25 minutes, then taking a 5-minute break", "Completing one task per day only", "Grouping all similar tasks into one long session"], "correct": 1},
            {"q": "'Time blocking' means:", "opts": ["Refusing to schedule any free time", "Scheduling specific blocks of time for specific tasks in your calendar", "Working on a task only when you feel motivated", "Blocking distracting websites during study"], "correct": 1},
            {"q": "Which of the following is an example of a SMART goal?", "opts": ["I want to be better at maths.", "I'll study more often.", "I should read books.", "I will complete two chapters of my science textbook every day for the next two weeks."], "correct": 3},
            {"q": "Multitasking is generally considered:", "opts": ["The most efficient way to work", "Essential for managing a busy schedule", "Less effective than focusing on one task at a time, as it reduces quality", "A skill all successful people use constantly"], "correct": 2},
            {"q": "'Batching' similar tasks together helps because:", "opts": ["It makes tasks take longer", "It reduces the mental effort of constantly switching between different types of work", "It forces you to multitask effectively", "It eliminates the need for breaks"], "correct": 1},
            {"q": "What is the purpose of a 'weekly review' in time management?", "opts": ["To punish yourself for tasks not completed", "To reflect on what was accomplished, identify gaps, and plan the coming week", "To delete old to-do lists", "To share your schedule with others"], "correct": 1},
            {"q": "Which strategy best helps overcome procrastination?", "opts": ["Waiting until you feel completely motivated", "Breaking a large task into small, manageable steps and starting with the first one", "Rewarding yourself before completing the task", "Doing easier tasks first and hoping motivation builds"], "correct": 1},
            {"q": "'Eating the frog' is a time management concept that means:", "opts": ["Eating a healthy breakfast before studying", "Tackling your most difficult or dreaded task first thing in the day", "Completing the shortest task first", "Taking a break before starting work"], "correct": 1},
        ],
        [
            {"q": "Long-term planning in time management involves:", "opts": ["Planning only the next 24 hours", "Setting goals and mapping out tasks weeks, months, or years in advance", "Avoiding flexibility in your schedule", "Only planning when a deadline is near"], "correct": 1},
            {"q": "Which best describes 'opportunity cost' in time management?", "opts": ["The financial cost of wasted time", "The value of what you give up when you choose to spend time on one activity over another", "The benefit of completing a task early", "The cost of scheduling tools and planners"], "correct": 1},
            {"q": "Flow state, as it relates to productivity, means:", "opts": ["Working at a slow, steady pace", "Being so deeply engaged in a task that time seems to pass quickly and performance is at its peak", "Moving between tasks without stopping", "Feeling relaxed during a break"], "correct": 1},
            {"q": "Digital tools like apps and calendars are most effective when:", "opts": ["Used only when you feel like it", "Shared with everyone around you", "Used consistently and integrated into a daily planning routine", "Replaced with a new app every week"], "correct": 2},
            {"q": "A student with multiple exams in one week should:", "opts": ["Study for all subjects simultaneously", "Focus on only the first exam and ignore the rest", "Create a study schedule that allocates time to each subject based on difficulty and exam date", "Study the night before each exam only"], "correct": 2},
            {"q": "Which mindset most supports excellent long-term time management?", "opts": ["I work better under pressure, so I'll wait.", "Time management is only for busy adults.", "Consistent small efforts compounded over time lead to big results.", "I can always catch up later."], "correct": 2},
            {"q": "Saying 'no' to non-essential commitments is a sign of:", "opts": ["Being antisocial and uncooperative", "Healthy boundary-setting and respect for your own time and priorities", "Poor leadership and teamwork", "Laziness"], "correct": 1},
            {"q": "Which is the best way to manage unexpected tasks that arise during your day?", "opts": ["Abandon your current plan entirely", "Ignore unexpected tasks until tomorrow", "Assess urgency, slot them into your schedule appropriately, and adjust other tasks if needed", "Always complete unexpected tasks before planned ones"], "correct": 2},
            {"q": "Time auditing means:", "opts": ["Having someone else check your schedule", "Tracking how you actually spend your time to identify inefficiencies and improve habits", "Deleting tasks you did not complete", "Estimating how long tasks will take without tracking them"], "correct": 1},
            {"q": "The most important long-term benefit of strong time management skills is:", "opts": ["Always finishing work before everyone else", "Never needing to ask for help", "Reduced stress, greater achievement, and more time for things that truly matter", "Having a perfectly structured every day with no flexibility"], "correct": 2},
        ],
    ],
    "Teamwork": [
        [
            {"q": "Teamwork is best defined as:", "opts": ["One person doing all the work for the group", "A group of people working together towards a shared goal", "Competing with others to produce the best individual result", "Dividing a task so each person works completely independently"], "correct": 1},
            {"q": "Which behaviour best supports a positive team environment?", "opts": ["Taking credit for others' ideas", "Encouraging and supporting team members", "Working alone to avoid conflict", "Always leading, never following"], "correct": 1},
            {"q": "What is the most important foundation of any successful team?", "opts": ["Having the smartest members", "Trust among team members", "Having the same personality type", "Competing against each other"], "correct": 1},
            {"q": "In a group project, what should you do if you disagree with a teammate's idea?", "opts": ["Ignore their idea and do it your way", "Respectfully share your perspective and listen to theirs", "Complain to the teacher immediately", "Stay silent to avoid conflict"], "correct": 1},
            {"q": "What does 'pulling your weight' in a team mean?", "opts": ["Being the strongest physically", "Contributing your fair share of effort to the team's work", "Leading the team at all times", "Completing other people's tasks for them"], "correct": 1},
            {"q": "Which is a sign of a dysfunctional team?", "opts": ["Open and honest communication", "Clear roles and responsibilities", "Team members frequently blaming each other for mistakes", "Sharing credit for successes"], "correct": 2},
            {"q": "Effective teams make decisions by:", "opts": ["Always following the most popular opinion", "Having one person decide everything", "Discussing options and reaching a conclusion that considers everyone's input", "Voting without any discussion"], "correct": 2},
            {"q": "Which of the following is an example of a team norm?", "opts": ["Individual grades for each member", "An agreed rule that all members will respond to messages within 24 hours", "The team leader's personal preferences", "A competition between members for the best performance"], "correct": 1},
            {"q": "Why is celebrating team success important?", "opts": ["It wastes time that could be used for more work", "It boosts morale, reinforces positive behaviours, and strengthens team bonds", "It only benefits the leader", "It is only necessary in professional settings"], "correct": 1},
            {"q": "What is the role of a 'follower' in a team?", "opts": ["To do whatever the leader says without question", "To have no real impact on the team", "To contribute actively, support the team's direction, and provide honest feedback", "To wait for instructions before doing anything"], "correct": 2},
        ],
        [
            {"q": "Tuckman's stages of team development are:", "opts": ["Plan, Execute, Review, Improve", "Forming, Storming, Norming, Performing", "Meet, Assign, Work, Submit", "Agree, Collaborate, Complete, Celebrate"], "correct": 1},
            {"q": "During the 'storming' stage of team development, teams typically experience:", "opts": ["High productivity and smooth collaboration", "Conflict and tension as members assert their roles and ideas", "A clear and agreed team structure", "The completion of the final project"], "correct": 1},
            {"q": "Diversity in a team is valuable because:", "opts": ["It always makes teams slower", "Different perspectives, skills, and experiences lead to more creative and effective solutions", "It reduces the need for communication", "Homogeneous teams always outperform diverse ones"], "correct": 1},
            {"q": "Which conflict resolution strategy seeks a solution where all parties benefit?", "opts": ["Avoidance", "Accommodation", "Competition", "Collaboration (win-win)"], "correct": 3},
            {"q": "In a high-performing team, roles are important because they:", "opts": ["Restrict what members can contribute", "Clarify responsibilities and reduce duplication of effort", "Guarantee that all members do the same amount of work", "Give the leader complete authority over others"], "correct": 1},
            {"q": "What is 'groupthink' and why is it a problem?", "opts": ["A creative brainstorming technique", "When the desire for group harmony overrides critical thinking, leading to poor decisions", "When all group members think at the same speed", "A method of dividing intellectual tasks equally"], "correct": 1},
            {"q": "Active participation in a team meeting includes:", "opts": ["Attending but staying silent", "Sharing ideas, listening to others, and contributing to decisions", "Completing your own work during the meeting", "Agreeing with everything to keep the peace"], "correct": 1},
            {"q": "Accountability in a team means:", "opts": ["Only the leader is responsible for outcomes", "Every member takes responsibility for their own contributions and commitments", "Blaming individuals when targets are missed", "Keeping performance private"], "correct": 1},
            {"q": "Peer feedback within a team should be:", "opts": ["Only given after the project is complete", "Regular, specific, respectful, and focused on improvement", "Shared only with the team leader, never directly", "Always positive to protect team morale"], "correct": 1},
            {"q": "A team that is 'interdependent' means:", "opts": ["Each member works completely independently", "Members rely on each other's contributions to achieve the shared goal", "The team has no need for a leader", "Only the strongest members carry the team"], "correct": 1},
        ],
        [
            {"q": "Cross-functional teams are composed of:", "opts": ["Members from the same department with the same skills", "Members from different areas of expertise working towards a common goal", "Teams that work across different time zones only", "Teams led by multiple leaders simultaneously"], "correct": 1},
            {"q": "Psychological safety in a team environment means:", "opts": ["Physical safety in the workplace", "Team members feel safe to take risks, voice opinions, and make mistakes without fear of judgment", "Keeping all feedback confidential", "Protecting the team from external criticism"], "correct": 1},
            {"q": "The most effective way to manage a remote or hybrid team:", "opts": ["Assume everyone is working and check in only at the end", "Establish clear communication channels, regular check-ins, and shared collaboration tools", "Have all remote members work the same hours regardless of time zone", "Only meet in person and avoid digital communication"], "correct": 1},
            {"q": "When a team consistently underperforms, the first step should be to:", "opts": ["Replace the weakest members immediately", "Diagnose the root causes through honest team reflection and data", "Increase the number of team meetings", "Assign stricter deadlines"], "correct": 1},
            {"q": "Shared leadership in advanced teamwork means:", "opts": ["Having two team leaders with equal authority", "Leadership responsibilities shifting between members based on the task and strengths", "Voting for a new leader each week", "Removing the formal leader role entirely"], "correct": 1},
            {"q": "How does a strong team culture impact performance?", "opts": ["It has little impact on actual results", "It creates a sense of belonging and shared purpose, driving motivation and higher performance", "It makes teams less flexible and innovative", "It only benefits large teams"], "correct": 1},
            {"q": "In high-stakes collaborative projects, the most important factor is:", "opts": ["Individual recognition for each contribution", "Alignment on shared goals, clear roles, and open communication", "Having the most experienced team members", "Using the latest technology tools"], "correct": 1},
            {"q": "When integrating new members into an established team, leaders should:", "opts": ["Expect new members to adapt immediately without support", "Provide onboarding, introduce team norms, and create opportunities for connection", "Allow new members to create their own team culture", "Assign new members only low-priority tasks indefinitely"], "correct": 1},
            {"q": "'Collective intelligence' in teamwork refers to:", "opts": ["Each member having a high IQ", "The combined knowledge and problem-solving capacity of the group, which exceeds individual ability", "Sharing study notes before an exam", "Appointing the smartest member as the permanent decision-maker"], "correct": 1},
            {"q": "A retrospective meeting is used to:", "opts": ["Plan the next project's timeline", "Reflect on what went well, what didn't, and how the team can improve going forward", "Assign blame for project failures", "Celebrate only positive achievements"], "correct": 1},
        ],
    ],
    "Creativity": [
        [
            {"q": "Creativity is best defined as:", "opts": ["The ability to draw and paint well", "The ability to generate new, original, and useful ideas or solutions", "Copying ideas from others and improving them slightly", "A talent only some people are born with"], "correct": 1},
            {"q": "Which mindset best supports creativity?", "opts": ["There is only one right answer.", "I can explore many possibilities and learn from failure.", "I am not a creative person.", "Creative ideas come only during inspiration."], "correct": 1},
            {"q": "Brainstorming is most effective when:", "opts": ["You immediately judge each idea as it comes", "All ideas are welcome without judgment to encourage free thinking", "Only the leader generates ideas", "You focus on only one possible solution"], "correct": 1},
            {"q": "Which of the following is an example of creative thinking?", "opts": ["Memorising answers from a textbook", "Repeating a process exactly as instructed", "Designing a new solution to a problem using unexpected materials", "Following a recipe without any variation"], "correct": 2},
            {"q": "Curiosity supports creativity because:", "opts": ["It wastes time on unimportant questions", "Asking 'why' and 'what if' opens up new possibilities and unexpected connections", "It leads to distraction and unfocused work", "Curious people rarely complete tasks"], "correct": 1},
            {"q": "Play and experimentation are important to creativity because:", "opts": ["They have no connection to serious creative work", "They encourage risk-taking, exploration, and discovery without fear of failure", "They are only appropriate for young children", "They slow down the creative process"], "correct": 1},
            {"q": "Which of the following best describes 'thinking outside the box'?", "opts": ["Solving problems using only established methods", "Avoiding structure entirely", "Approaching a problem from an unconventional angle or perspective", "Ignoring the rules completely"], "correct": 2},
            {"q": "A creative person who experiences a 'mental block' should:", "opts": ["Give up on the task", "Take a break, change environment, or approach the problem from a different angle", "Force themselves to keep working until inspiration arrives", "Copy someone else's idea"], "correct": 1},
            {"q": "Which of the following is NOT a creative skill?", "opts": ["Imagination", "Problem-solving", "Memorising facts without applying them", "Flexible thinking"], "correct": 2},
            {"q": "Creative confidence means:", "opts": ["Believing your first idea is always the best", "Trusting yourself to generate ideas and being willing to share them despite uncertainty", "Never asking for feedback on your work", "Only creating when you feel completely inspired"], "correct": 1},
        ],
        [
            {"q": "Divergent thinking involves:", "opts": ["Narrowing options to one correct answer", "Generating many possible ideas or solutions to an open-ended problem", "Following a single proven process", "Analysing data to find patterns"], "correct": 1},
            {"q": "Convergent thinking is best used when:", "opts": ["You are in the early stages of brainstorming", "You need to evaluate ideas and select the best solution from existing options", "You want to generate as many ideas as possible", "You are working on an open-ended creative project"], "correct": 1},
            {"q": "The SCAMPER technique stands for:", "opts": ["Stop, Create, Analyse, Make, Plan, Evaluate, Redo", "Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse", "Search, Compare, Arrange, Measure, Produce, Expand, Reflect", "Study, Categorise, Apply, Model, Practice, Experiment, Review"], "correct": 1},
            {"q": "Which best describes 'creative risk-taking'?", "opts": ["Acting recklessly without thinking about consequences", "Trying a new approach despite the possibility of failure, in order to discover something better", "Only presenting ideas you are completely certain about", "Copying a proven idea to guarantee success"], "correct": 1},
            {"q": "Constraints (limitations) in a creative project can:", "opts": ["Only hinder creativity and produce worse results", "Stimulate creativity by forcing you to find innovative solutions within defined boundaries", "Be ignored without affecting the outcome", "Never lead to better results than total freedom"], "correct": 1},
            {"q": "Collaboration enhances creativity because:", "opts": ["One person's idea is always better than a group's", "Diverse perspectives combine to produce ideas no individual would reach alone", "Groups always agree, making the process more efficient", "It reduces the need for individual creative thinking"], "correct": 1},
            {"q": "Design thinking is a creative problem-solving process that begins with:", "opts": ["Prototyping a solution immediately", "Testing your first idea", "Empathising with the user to deeply understand their needs and challenges", "Brainstorming solutions before understanding the problem"], "correct": 2},
            {"q": "An 'iterative' creative process means:", "opts": ["Creating one version and finalising it immediately", "Continuously improving a design through repeated cycles of testing, feedback, and refinement", "Avoiding feedback from others during the creative process", "Starting from scratch every time you encounter a problem"], "correct": 1},
            {"q": "How does exposure to diverse experiences enhance creativity?", "opts": ["It confuses creative thinking", "It builds a wider bank of ideas and connections that can be combined in novel ways", "It is only useful for artists and designers", "Focused, narrow experience is always more valuable"], "correct": 1},
            {"q": "'Incubation' in the creative process refers to:", "opts": ["The final stage of completing a creative project", "A period of stepping away from a problem, during which the subconscious mind continues working on it", "The first burst of inspiration at the start of a project", "Organising and presenting your final creative work"], "correct": 1},
        ],
        [
            {"q": "Innovation differs from creativity in that:", "opts": ["They are exactly the same thing", "Creativity is only for art; innovation is for business", "Creativity generates new ideas; innovation turns those ideas into practical, implemented solutions", "Innovation requires no creative thinking"], "correct": 2},
            {"q": "Systems thinking in creativity involves:", "opts": ["Following a rigid set of steps to generate ideas", "Understanding how different elements of a problem are interconnected and how changing one affects others", "Breaking a problem into completely separate, unrelated parts", "Using technology to automate the creative process"], "correct": 1},
            {"q": "Which best describes a 'growth mindset' in relation to creativity?", "opts": ["My creative ability is fixed and cannot change.", "Every creative challenge is an opportunity to learn, grow, and improve.", "I should only attempt creative tasks I already know I can do.", "Failure means I am not creative enough."], "correct": 1},
            {"q": "Lateral thinking refers to:", "opts": ["Logical step-by-step reasoning towards a solution", "Solving problems through indirect, non-obvious approaches and creative reframing", "Thinking at the same level as others in your field", "Avoiding all structured thinking processes"], "correct": 1},
            {"q": "When pitching a creative idea, the most important element is:", "opts": ["Using the most complex language possible to sound impressive", "Clearly communicating the problem it solves and why it matters to the audience", "Presenting as many ideas as possible to show range", "Focusing only on the aesthetics of the final product"], "correct": 1},
            {"q": "How can failure contribute to the creative process?", "opts": ["It should always be avoided as it wastes time", "It provides critical insights into what doesn't work, guiding refinement and better solutions", "Failure only occurs when the creative process is poorly managed", "It has no real value in a professional creative environment"], "correct": 1},
            {"q": "Sustainable creativity means:", "opts": ["Making art using recycled materials", "Building habits and environments that allow for consistent creative output over the long term, without burnout", "Creating solutions that are environmentally friendly", "Limiting your creativity to avoid wasting energy"], "correct": 1},
            {"q": "The concept of 'creative capital' refers to:", "opts": ["The budget available for a creative project", "The accumulated knowledge, skills, experiences, and networks that fuel creative output", "The number of creative projects completed", "Financial investment in the arts"], "correct": 1},
            {"q": "In which scenario is creative thinking most critical?", "opts": ["Completing a well-defined, repetitive task", "Following a strict set of pre-existing instructions", "Addressing a complex, ambiguous problem where no established solution exists", "Memorising and applying a known formula"], "correct": 2},
            {"q": "A culture of creativity in an organisation is built by:", "opts": ["Rewarding only successful outcomes and penalising all failures", "Encouraging experimentation, tolerating failure, celebrating diverse ideas, and providing psychological safety", "Appointing one designated creative person to generate all ideas", "Strictly following established processes and discouraging deviation"], "correct": 1},
        ],
    ],
    "Critical Thinking": [
        [
            {"q": "Critical thinking is best defined as:", "opts": ["Being critical or negative about everything", "Accepting information from experts without question", "Objectively analysing and evaluating information to form a reasoned judgement", "Memorising facts and recalling them accurately"], "correct": 2},
            {"q": "A reliable source of information is one that is:", "opts": ["Popular and widely shared on social media", "Accurate, credible, evidence-based, and from a trusted author or institution", "The first result that appears on a search engine", "One that confirms what you already believe"], "correct": 1},
            {"q": "What is a 'fact' in critical thinking?", "opts": ["Something many people believe to be true", "A statement that can be verified and proven with evidence", "An expert's personal opinion", "Any claim made in a textbook"], "correct": 1},
            {"q": "What is an 'opinion'?", "opts": ["A statement supported by data and evidence", "A personal view or judgement that may not be based on verifiable facts", "A fact that has not yet been proven", "A conclusion reached through logical reasoning only"], "correct": 1},
            {"q": "Asking 'What is the evidence for this claim?' is an example of:", "opts": ["Being unnecessarily skeptical", "Critical thinking in action", "Rudely questioning authority", "Wasting time on obvious answers"], "correct": 1},
            {"q": "Confirmation bias means:", "opts": ["Confirming information from multiple sources", "Being confident in your conclusions", "The tendency to search for and favour information that confirms your existing beliefs", "A method of double-checking your reasoning"], "correct": 2},
            {"q": "Which of the following is an example of a logical fallacy?", "opts": ["Providing statistical evidence for your argument", "Acknowledging the limits of your knowledge", "Everyone believes this, so it must be true. (Appeal to Popularity)", "Considering multiple perspectives before concluding"], "correct": 2},
            {"q": "When evaluating an argument, you should first look for:", "opts": ["Whether the conclusion sounds impressive", "Whether the evidence clearly and logically supports the conclusion", "Whether you personally agree with it", "Whether it was written by a famous person"], "correct": 1},
            {"q": "What does it mean to 'think for yourself' in critical thinking?", "opts": ["Always disagree with others to show independence", "Form your own reasoned conclusions based on evidence rather than blindly following others", "Never consult other sources or people", "Trust only your intuition"], "correct": 1},
            {"q": "Which question is the BEST example of critical thinking?", "opts": ["Who wrote this article?", "How long is this text?", "Is the reasoning in this argument logical, and is it supported by credible evidence?", "Do I find this topic interesting?"], "correct": 2},
        ],
        [
            {"q": "Inductive reasoning involves:", "opts": ["Starting with a general rule and applying it to a specific case", "Drawing general conclusions from specific observations and evidence", "Accepting a conclusion without examining the evidence", "Reversing a logical argument to test it"], "correct": 1},
            {"q": "Deductive reasoning involves:", "opts": ["Starting with a general principle and applying it to reach a specific, logical conclusion", "Gathering evidence from observations to form a hypothesis", "Brainstorming many possible explanations for a problem", "Relying on instinct to make decisions"], "correct": 0},
            {"q": "A 'straw man' fallacy involves:", "opts": ["Building a weak argument to test your own reasoning", "Using physical props to explain an argument", "Misrepresenting someone's argument in a weakened form in order to more easily refute it", "Presenting an argument without any evidence"], "correct": 2},
            {"q": "Which best demonstrates sound critical analysis?", "opts": ["Accepting the first explanation that makes sense", "Examining multiple perspectives, testing assumptions, and evaluating evidence before concluding", "Relying on the most popular viewpoint", "Trusting emotional reactions as a guide to truth"], "correct": 1},
            {"q": "What is an 'assumption' in critical thinking?", "opts": ["A proven fact used to support a conclusion", "An unstated belief taken for granted that underpins an argument without being verified", "A conclusion drawn from careful analysis", "A question asked to clarify an argument"], "correct": 1},
            {"q": "The Socratic method involves:", "opts": ["Lecturing students with expert knowledge", "Using a series of probing questions to stimulate critical thinking and uncover assumptions", "Accepting authoritative answers without question", "Debating to win rather than to discover truth"], "correct": 1},
            {"q": "Which approach best helps identify biases in a source?", "opts": ["Checking how recently it was published", "Examining the author's background, the source's funding, and comparing it with other viewpoints", "Counting how many times an argument is repeated", "Seeing how many other sources link to it"], "correct": 1},
            {"q": "'Correlation does not imply causation' means:", "opts": ["Two things that are related must have caused each other", "Just because two things occur together does not mean one caused the other", "Statistical data is never reliable", "Causes and effects are always easy to identify"], "correct": 1},
            {"q": "An 'ad hominem' fallacy attacks:", "opts": ["The logic of an argument", "The evidence presented", "The person making the argument rather than the argument itself", "The conclusion of a debate"], "correct": 2},
            {"q": "What is 'evidence-based reasoning'?", "opts": ["Forming a conclusion and then searching for evidence to support it", "Drawing conclusions based on verifiable, relevant, and sufficient evidence", "Trusting expert opinions without question", "Using the most emotionally compelling information available"], "correct": 1},
        ],
        [
            {"q": "Systems thinking involves:", "opts": ["Analysing each part of a problem in isolation", "Understanding how the components of a complex system interact and influence each other", "Finding the single root cause of any problem", "Applying a fixed process to all problems"], "correct": 1},
            {"q": "Which best describes 'metacognition' in the context of critical thinking?", "opts": ["Thinking about other people's thought processes", "Reflecting on and monitoring your own thinking, reasoning, and assumptions", "Using logic to solve abstract mathematical problems", "Learning from textbooks rather than experience"], "correct": 1},
            {"q": "When analysing complex data, a critical thinker should:", "opts": ["Accept the first pattern they notice", "Look for alternative explanations, identify outliers, and consider limitations of the data", "Rely solely on visual representations without examining raw numbers", "Trust the source's own interpretation of the data"], "correct": 1},
            {"q": "Ethical reasoning in critical thinking requires:", "opts": ["Always following the law, regardless of moral considerations", "Evaluating decisions based on principles of fairness, rights, and consequences for all affected parties", "Making the choice that benefits you most", "Deferring all ethical judgements to authority"], "correct": 1},
            {"q": "The 'devil's advocate' approach in critical thinking is useful because:", "opts": ["It is a way of expressing genuine disagreement", "Deliberately arguing against a position helps identify weaknesses and strengthen conclusions", "It slows down decision-making unnecessarily", "It guarantees a better final answer"], "correct": 1},
            {"q": "Which is the most important skill for navigating information overload?", "opts": ["Reading everything available on a topic", "Evaluating source credibility, filtering for relevance, and synthesising key insights", "Trusting algorithms to curate information for you", "Only reading one trusted source exclusively"], "correct": 1},
            {"q": "When a problem has no clear correct answer, the best approach is to:", "opts": ["Avoid making any decision", "Apply structured reasoning, consider trade-offs, and make the best-supported decision given available evidence", "Choose the option most people agree with", "Defer the decision indefinitely until more information is available"], "correct": 1},
            {"q": "'Intellectual humility' in critical thinking means:", "opts": ["Never expressing confidence in your conclusions", "Acknowledging the limits of your knowledge and remaining open to changing your views when confronted with better evidence", "Always agreeing with experts", "Avoiding debates to protect your opinions"], "correct": 1},
            {"q": "Second-order thinking involves:", "opts": ["Considering only the immediate consequences of a decision", "Thinking beyond immediate consequences to anticipate longer-term and indirect effects of a decision", "Repeating a thought process a second time to confirm it", "Consulting a second person before deciding"], "correct": 1},
            {"q": "The most important outcome of developing strong critical thinking skills is:", "opts": ["Winning every argument you participate in", "Always reaching the correct conclusion", "Making better, more informed decisions and being able to navigate complex information with clarity", "Never being wrong"], "correct": 2},
        ],
    ],
    "Adaptability": [
        [
            {"q": "Adaptability is best defined as:", "opts": ["Changing your personality to please others", "The ability to adjust effectively to new conditions, challenges, or environments", "Refusing to change your habits regardless of circumstances", "Being flexible only when it benefits you"], "correct": 1},
            {"q": "Why is adaptability important for students?", "opts": ["It helps them avoid all challenges", "It enables them to handle unexpected changes in school, relationships, and life with resilience", "It guarantees they will always succeed", "It means they never need to plan ahead"], "correct": 1},
            {"q": "Which of the following is an example of adaptability?", "opts": ["Refusing to change study methods even when they are not working", "Switching to a new strategy when your original plan is not producing results", "Always following the same routine regardless of changing circumstances", "Avoiding new environments because they are uncomfortable"], "correct": 1},
            {"q": "A growth mindset supports adaptability because:", "opts": ["It encourages seeing challenges as opportunities to learn rather than threats to avoid", "It means you never experience failure", "It removes all stress from difficult situations", "It makes change feel completely comfortable instantly"], "correct": 0},
            {"q": "When faced with an unexpected change, the first healthy response is to:", "opts": ["Panic and search for someone to blame", "Avoid the situation until it resolves itself", "Acknowledge the change, manage your reaction, and look for constructive ways to respond", "Immediately revert to the most familiar behaviour"], "correct": 2},
            {"q": "Resilience and adaptability are connected because:", "opts": ["They are exactly the same skill", "Resilience helps you recover from setbacks, which is necessary for adapting to new situations", "You need resilience only when things go well", "Adaptability means you never need resilience"], "correct": 1},
            {"q": "Which scenario demonstrates adaptability in a school setting?", "opts": ["Repeating the same study approach despite failing multiple tests", "Changing your revision strategy after identifying that your current method is ineffective", "Refusing to work with new group members", "Avoiding any subject that feels difficult"], "correct": 1},
            {"q": "What does it mean to 'embrace change'?", "opts": ["Pretending change doesn't affect you", "Accepting every change without ever questioning it", "Approaching change with openness, curiosity, and a willingness to learn from new experiences", "Changing as slowly as possible to minimise discomfort"], "correct": 2},
            {"q": "Which is a common barrier to adaptability?", "opts": ["Self-awareness", "Fear of the unknown and discomfort with uncertainty", "A willingness to learn new skills", "Open-mindedness"], "correct": 1},
            {"q": "A student who adapts well to a new school demonstrates:", "opts": ["That they have no attachment to their old school", "Flexibility, openness, and the ability to build new connections while maintaining their identity", "That they never felt comfortable at their old school", "That change is always easy for them"], "correct": 1},
        ],
        [
            {"q": "Cognitive flexibility refers to:", "opts": ["Physical flexibility and body movement", "The mental ability to shift perspectives, approaches, and strategies when circumstances change", "Memorising large amounts of information quickly", "Focusing deeply on one subject for a long time"], "correct": 1},
            {"q": "How does self-regulation contribute to adaptability?", "opts": ["It keeps your emotions completely suppressed", "It helps you manage emotional reactions to change, allowing you to respond thoughtfully rather than reactively", "It ensures you never feel stressed", "It removes the need for flexibility"], "correct": 1},
            {"q": "When a plan fails unexpectedly, the most adaptive response is to:", "opts": ["Abandon all plans in the future", "Analyse what went wrong, learn from it, and develop a revised approach", "Pretend the plan succeeded", "Blame external factors entirely"], "correct": 1},
            {"q": "'Unlearning' in the context of adaptability means:", "opts": ["Forgetting all previously learned knowledge", "Letting go of outdated beliefs, habits, or methods that are no longer effective in new contexts", "Refusing to learn new skills", "Returning to basic education"], "correct": 1},
            {"q": "Which characteristic distinguishes highly adaptable people from others?", "opts": ["They are never affected by stress or change", "They avoid all situations that require change", "They proactively seek and respond to feedback, continuously adjusting their approach", "They make decisions slowly to avoid any mistakes"], "correct": 2},
            {"q": "Adaptability in group work means:", "opts": ["Always imposing your approach on the group", "Adjusting your working style to suit different teammates, tasks, and circumstances", "Changing your opinions to avoid conflict", "Letting others make all the decisions"], "correct": 1},
            {"q": "Which is an example of proactive adaptability?", "opts": ["Waiting for a crisis before making any changes", "Responding to feedback only when required to", "Anticipating future changes and preparing in advance to respond effectively", "Avoiding new experiences to remain comfortable"], "correct": 2},
            {"q": "Stress management is a component of adaptability because:", "opts": ["Stress is not related to adaptability", "Managing stress allows you to think clearly and make effective decisions even in challenging circumstances", "Adapting always eliminates all stress", "Highly adaptable people never experience stress"], "correct": 1},
            {"q": "Which mindset best enables adaptability in the face of failure?", "opts": ["Failure means I am not capable.", "I should avoid any situation where I might fail.", "Failure is information that helps me improve and adapt.", "If my first approach fails, nothing will work."], "correct": 2},
            {"q": "How does adaptability relate to long-term career success?", "opts": ["It is only relevant during major life changes", "Career paths are stable, so adaptability is less important", "The modern world changes rapidly, and adaptable individuals can navigate evolving industries effectively", "Technical skills alone are sufficient for career success"], "correct": 2},
        ],
        [
            {"q": "Adaptive expertise is different from routine expertise in that:", "opts": ["Routine experts perform better in all situations", "Adaptive experts can apply their knowledge creatively in novel, unfamiliar situations beyond their experience", "Adaptive experts know fewer facts than routine experts", "Routine expertise requires continuous learning; adaptive expertise does not"], "correct": 1},
            {"q": "In rapidly changing environments, which skill complements adaptability most?", "opts": ["Strict routine and habit", "Continuous learning and a commitment to updating your knowledge and skills", "Avoiding all risk", "Specialising in one narrow area only"], "correct": 1},
            {"q": "The concept of 'pivot' in adaptability refers to:", "opts": ["Returning to a previous approach when the current one is difficult", "Making a significant, strategic change in direction in response to new information or a change in circumstances", "Gradually adjusting a strategy over a long period", "Completely abandoning a goal when obstacles arise"], "correct": 1},
            {"q": "Which best describes 'ambiguity tolerance' in adaptability?", "opts": ["Avoiding any unclear situations", "The ability to function effectively and make decisions even when information is incomplete or uncertain", "Feeling completely comfortable with every uncertain situation", "Waiting until all information is available before acting"], "correct": 1},
            {"q": "Cultural adaptability involves:", "opts": ["Abandoning your own cultural identity when abroad", "Navigating and communicating effectively across different cultural norms, values, and expectations", "Assuming all cultures operate the same way", "Adapting only your language when in a different cultural environment"], "correct": 1},
            {"q": "Why is self-awareness a prerequisite for advanced adaptability?", "opts": ["Self-aware people never make mistakes", "Knowing your strengths, weaknesses, and triggers helps you identify when and how to adapt most effectively", "Self-awareness eliminates the need to seek feedback from others", "It is not actually related to adaptability"], "correct": 1},
            {"q": "Transformative adaptation means:", "opts": ["Making small, incremental adjustments to existing plans", "Returning to a prior state after a temporary change", "Using challenges and disruptions as catalysts to fundamentally reimagine and improve your approach", "Adapting only when forced to by external circumstances"], "correct": 2},
            {"q": "Which is a sign of highly developed adaptability?", "opts": ["Feeling uncomfortable and resisting change in all situations", "Remaining calm, curious, and solution-focused when confronted with major disruptions", "Avoiding all planning because plans always change", "Always following the same approach regardless of the situation"], "correct": 1},
            {"q": "How can reflecting on past adaptations improve future adaptability?", "opts": ["It has no meaningful impact on future behaviour", "It helps identify which strategies worked, builds confidence, and creates a toolkit of approaches for new challenges", "It only reinforces mistakes", "Reflection should only be done immediately after a situation, not later"], "correct": 1},
            {"q": "The ultimate goal of developing adaptability is:", "opts": ["Never feeling stress or uncertainty again", "Being able to succeed only in familiar environments", "Changing your core identity to fit every new situation", "Building the capacity to thrive in an uncertain, ever-changing world while staying grounded in your values and purpose"], "correct": 3},
        ],
    ],
}

async def seed_mcqs():
    async with AsyncSessionLocal() as db:
        print("Starting MCQ seeding...")
        total_added = 0

        for skill_name, modules_questions in MCQ_BANK.items():
            # Find the skill
            res = await db.execute(select(Skill).where(Skill.name == skill_name))
            skill = res.scalar_one_or_none()
            if not skill:
                print(f"  ⚠ Skill '{skill_name}' not found. Run seed_all.py first.")
                continue

            # Get modules ordered by order_index
            res2 = await db.execute(
                select(SkillModule)
                .where(SkillModule.skill_id == skill.id)
                .order_by(SkillModule.order_index)
            )
            modules = res2.scalars().all()

            for mod_idx, questions in enumerate(modules_questions):
                if mod_idx >= len(modules):
                    print(f"  ⚠ Module index {mod_idx} out of range for skill '{skill_name}'")
                    continue
                module = modules[mod_idx]

                # Check if quiz already exists for this module
                res3 = await db.execute(select(Quiz).where(Quiz.module_id == module.id))
                existing_quiz = res3.scalar_one_or_none()

                # Delete old quiz for this module to ensure clean seed
                if existing_quiz:
                    await db.execute(
                        delete(QuizQuestion).where(QuizQuestion.quiz_id == existing_quiz.id)
                    )
                    quiz = existing_quiz
                    quiz.title = f"{module.title} Final Exam"
                    quiz.description = f"Test your mastery of {module.title}. You need 70% to pass."
                    quiz.pass_percentage = 70.0
                else:
                    quiz = Quiz(
                        id=str(uuid.uuid4()),
                        module_id=module.id,
                        title=f"{module.title} Final Exam",
                        description=f"Test your mastery of {module.title}. You need 70% to pass.",
                        pass_percentage=70.0,
                    )
                    db.add(quiz)
                    await db.flush()

                for q_idx, qdata in enumerate(questions):
                    q = QuizQuestion(
                        id=str(uuid.uuid4()),
                        quiz_id=quiz.id,
                        question_text=qdata["q"],
                        question_type="mcq",
                        order_index=q_idx,
                    )
                    db.add(q)
                    await db.flush()
                    for opt_idx, opt_text in enumerate(qdata["opts"]):
                        db.add(QuizOption(
                            id=str(uuid.uuid4()),
                            question_id=q.id,
                            option_text=opt_text,
                            is_correct=(opt_idx == qdata["correct"]),
                        ))
                    total_added += 1

                print(f"  ✅ {skill_name} / Module {mod_idx + 1} — {len(questions)} questions seeded")

        await db.commit()
        print(f"\n🎉 Done! Total questions seeded: {total_added}")

if __name__ == "__main__":
    asyncio.run(seed_mcqs())
