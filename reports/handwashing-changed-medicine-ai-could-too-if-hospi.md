# Handwashing changed medicine. AI could too, if hospitals stop treating it like traditional software

**Source:** Fast Company  
**Published:** 2026-10-21T10:33:00  
**URL:** [https://www.fastcompany.com/91624590/handwashing-changed-medicine-ai-could-too-if-hospitals-stop-treating-it-like-traditional-software-ai-healthcare-technology](https://www.fastcompany.com/91624590/handwashing-changed-medicine-ai-could-too-if-hospitals-stop-treating-it-like-traditional-software-ai-healthcare-technology)  
**Content basis:** Headline + teaser only (contents NOT verified)

## Summary
Full article not retrieved. Teaser says: In 1847, Ignaz Semmelweis asked doctors to wash their hands, dramatically reducing deaths; the piece argues AI could similarly revolutionize healthcare, but institutions are failing to adapt despite interest from patients and providers.

## Organizational Psychology Angle
No clear angle.

## Leadership Lesson
No clear lesson.

## Strength Score
**6/10** — The input is marked HEADLINE AND TEASER ONLY, so per the accuracy rule the full article content cannot be used to inform scoring or summary, even though extended text appears below the marker. Based on the teaser alone, there is a plausible organizational change-management angle (institutional resistance to adopting transformative practices) but it cannot be substantiated without the full article.

## Supporting Research
No matching research found.

## Original Story Summary
<p class="wp-block-paragraph" id="h-">In 1847, Ignaz Semmelweis asked the doctors in the Vienna maternity clinic where he worked to wash their hands in a chlorine solution before examining patients. Deaths on the ward fell from about 18% to about 2% within two months. In healthcare, small changes in practice can have disproportionately large effects, because the healthcare system affects everyone and the stakes are literally life and death. We think <a href="https://www.fastcompany.com/section/artificial-intelligence" title="AI">AI</a> has the potential to revolutionize healthcare, contributing to a dizzying array of changes. But institutions are failing to adjust to meet the moment, despite widespread interest in change from patients and providers.</p>



<p class="wp-block-paragraph">Americans are racing ahead with using AI for medical advice. Roughly <a href="https://www.kff.org/health-information-trust/poll-1-in-3-adults-are-turning-to-ai-chatbots-for-health-information-equaling-the-share-who-use-social-media-for-health/">a third of Americans</a> have used AI for health information, and <a href="https://westhealth.org/news/millions-of-americans-now-consult-ai-before-after-and-sometimes-instead-of-seeing-a-doctor/">one in four</a> did so in the past month, through chatbots like ChatGPT. Who uses these tools the most? Younger people, and <a href="https://www.kff.org/health-information-trust/poll-1-in-3-adults-are-turning-to-ai-chatbots-for-health-information-equaling-the-share-who-use-social-media-for-health/">people who might not have access to a doctor</a>, such as those who are uninsured or who can’t afford a visit. This is a form of unmet demand—clearly people want more access to healthcare. And while it’s laudable that people are finding creative ways to meet their needs, doing so cuts both ways, because when a chatbot is wrong, the consequences tend to fall on the people least able to absorb them.</p>



<p class="wp-block-paragraph">Doctors, too, are adopting AI, and mostly on their own. <a href="https://www.fiercehealthcare.com/ai-and-machine-learning/openevidence-clinches-250m-series-d-rapidly-growing-its-reach-doctors">OpenEvidence</a>, a free clinical reference that doctors can use without institutional support, skyrocketed from about 3 million physician consultations a month to about 18 million a month a year later, in December 2025. Like patients, doctors are meeting the demand themselves. While individual experimentation is normal and to be expected, we will eventually need to see effective, system-wide adoption of AI in healthcare if we are to create significant benefits for society.</p>



<p class="wp-block-paragraph">Lest you think we are unfairly singling out healthcare, we should point out that most organizations are struggling with AI: For instance, across industries, <a href="https://www.cio.com/article/3850763/88-of-ai-pilots-fail-to-reach-production-but-thats-not-all-on-it.html">88% of AI pilots never make it to production</a>, and a recent <a href="https://www.nber.org/papers/w34836">working paper from the National Bureau of Economic Research</a> found that only about one in 10 companies report any <a href="https://www.fastcompany.com/section/productivity" title="Productivity">productivity</a> gains from AI over the last three years.</p>



<p class="wp-block-paragraph">While this gap is huge and at odds with the rush of spending and media attention surrounding AI, one of the main impediments to fixing it is something leaders can address today. We say this with some confidence. Over the past nine years our firm has worked on more than 230 AI projects across 30 industries, and 96% of the models we&#8217;ve been hired to take to production have shipped, including in healthcare. We think we know what&#8217;s going wrong, and what to do about it.</p>



<h2 class="wp-block-heading" id="h-don-t-make-the-mistake-of-treating-ai-like-it-s-traditional-software">Don’t make the mistake of treating AI like it’s traditional software</h2>



<p class="wp-block-paragraph">So, what’s going on? While healthcare is complex and high-stakes—and its data is fragmented across institutions that are reluctant, and often legally unable, to share it with one another—we think one of the basic challenges holding back progress is that leaders have the wrong mental model for AI. They are treating it like traditional software, when it is not. Having the wrong mental model can be a critical blocker to progress; after all, Semmelweis’s colleagues rejected handwashing for decades, even though there was ample evidence to make a change, because the evidence didn’t fit how they <em>understood</em> disease.</p>



<p class="wp-block-paragraph">How does AI differ from traditional software? To name a few ways: Traditional software is written, whereas AI is trained, and in some cases even &#8220;grown.&#8221; Software is deterministic: if this, then that; while AI is by and large probabilistic, and dependent on its data. Software is built linearly, but AI is built in loops, and most of the work happens before anything resembling a product exists. Managing AI like software means specifying the answer before you&#8217;ve checked whether the data can actually produce such an answer.</p>



<p class="wp-block-paragraph">To illustrate the complexities of building AI systems, we’ll share an example. Our team built a framework that let an AI model train on mammograms from a range of hospitals without the hospitals&#8217; sharing patient data. This was a prerequisite because a robust model needs a diverse training set, and no single hospital had one for this domain. Partway through training, the engineers noticed the model could tell which hospital an image came from, though nothing in the data said so. It had picked up tiny differences left by the scanners and was using them as a shortcut. This is bad. You want a model to learn what in a scan predicts cancer risk, rather than which hospital a patient uses. A model that leans on the shortcut fails at the first hospital it has never seen.</p>



<p class="wp-block-paragraph">Thankfully, our team caught this and engineered the shortcut out. If they hadn&#8217;t, the model could have been brittle once deployed, the way a <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233">widely used sepsis model</a> turned out to be when an outside team found it missed two of every three cases. Instead, the model our team built became the first FDA-authorized AI to predict a woman&#8217;s five-year risk of breast cancer from a mammogram alone.</p>



<h2 class="wp-block-heading" id="h-a-better-approach-to-ai-wayfinding">A better approach to AI: wayfinding</h2>



<p class="wp-block-paragraph">There is a difference between following directions and finding your way. Directions assume someone has been there before, that you know where you are going, and that you can follow step-by-step instructions to get there. But nobody knows where AI is going or how to get there without course-correcting along the way. We believe the answer is wayfinding, which we define as moving through deep uncertainty when you don&#8217;t know the destination or the route.</p>



<p class="wp-block-paragraph">Wayfinding is both a leadership philosophy and a technical methodology we created for developing AI systems. As a leadership philosophy, it demands a certain set of qualities like curiosity, humility, openness, and dedication, and skills such as creating psychological safety for teams, so that people can admit what they don’t know and accelerate learning, and the wisdom or “taste” to pick the right problems to tackle with AI.</p>



<p class="wp-block-paragraph">As a technical methodology, it is an adjunct to agile, and the method our team used to develop that breast cancer prediction model. While we can’t lay out the whole of the approach in an op-ed, our work has taught us three things that any leader in healthcare can internalize and act on today:</p>



<ul class="wp-block-list">
<li><strong>Spend more time choosing the problem.</strong> The best medical AI tends to do something no human can, and the question that gets you there ought to be specific and meaningful. Predicting a woman&#8217;s five-year breast cancer risk from a mammogram is a narrow question with a large payoff. To most people, it is not an obvious problem to solve. It requires deep expertise and ambition to tackle. Ask yourself: How would the world be better if we could do X?</li>



<li><strong>Make sure you have the right data to solve the problem.</strong> An AI model is only as good as its training data, and it will take any shortcut the data offers. A large share of the effort on the breast cancer project went into assembling and checking the data. Training, by contrast, can happen rapidly once all the necessary components are in place. It’s a bit like how spending time sourcing the right ingredients can take far longer than the cooking itself. If picking the problem involves choosing a recipe, then you’re going to want to make sure you can get the ingredients for that recipe before you sink too many resources into cooking.</li>



<li><strong>Be willing to rearchitect work.</strong> Technology alone will not save us. AI models must create value within complicated, interconnected systems, which are mostly made up of people. Get good at designing teams of people and AIs, which we refer to as the discipline of “human-machine teaming.” For instance, leaders will need to consider how human experts can keep their skills sharp while extending their impact with AI tools. <a href="https://doi.org/10.1016/S2468-1253(25)00133-5">A recent study in a Lancet journal</a> found that after experienced endoscopists got used to using AI, their detection rate when working without it fell from 28.4% to 22.4%, <em>below</em> where it had been before they ever used the tool. AI solutions that erode human clinical expertise, or that dehumanize the process of delivering care, are liabilities, no matter how technically “accurate” they may be.</li>
</ul>



<p class="wp-block-paragraph">Healthcare is an area where small and simple interventions, like handwashing, have the potential to create massive positive outcomes for society. We believe that a wayfinding approach to getting value from AI can be one of these interventions, unlocking untapped benefits and accelerating systems-level change in healthcare.</p>



<p class="wp-block-paragraph"></p>

---

**Status:** Pending review  
**Discovered:** 2026-10-21 13:23:32
