# Digest videos with ease
A tool to assist with video selection and understanding.

```python
python3 digest.py https://www.youtube.com/watch?v=9bZkp7q19f0
```

What can you use this for?
 - Video summarization
 - Extracting a well-formatted video transcript
 - Deciding whether a video's worth watching
 - Analyzing the bias in a video
 - Everybody's different, try it out and see for yourself!


## Installation
```bash
git clone https://github.com/davidhaas6/digest.git
cd digest
python3 -m venv .venv
pip install -r requirements.txt
```

## Configuration
 - Tested and developed on Python 3.10.12
 - export OPENAI_API_KEY="your-api-key-here"
   - I recommend putting this in your venv's activation script, e.g. ./.venv/bin/activate
 - Install https://github.com/kkdai/youtube (technically optional, but strongly recommended)


## Example output:
```
python digest.py https://www.youtube.com/watch?v=77omYd0JOeA
[youtube] 77omYd0JOeA: Downloading webpage
[info] Writing video subtitles to: cache/77omYd0JOeA.en.vtt
Querying LLM...
Estimated processing time: 32 seconds
131% [00:42,  3.10%/s]
Actual processing time: 42 seconds

Input length: 7142 letters. Cleaned transcript length: 7059 letters

TLDR: The video details the engineering marvels of Venice, explaining how its founders transformed a marshy lagoon into a powerful city through innovative construction techniques, effective waste management, and clever water collection systems, all while overcoming significant environmental challenges.

Summary:
 The video begins by setting the historical context of Venice, stating, "The year is 452. The Roman Empire is on the brink of collapse, and the Huns have just launched their attack on Northern Italy." This dramatic backdrop highlights the urgency and necessity for the local population to seek refuge, leading them to the lagoon that would become Venice. The narrator emphasizes the remarkable transformation of this area, noting that despite having "no roads, no land, and no fresh water," the Venetians managed to create a thriving city from a "muddy swamp."

The engineering ingenuity of the Venetians is a central theme throughout the video. The narrator explains how the first settlers faced significant challenges due to the soft clay of the islands, stating, "The small, marshy islands were made of an incredibly soft clay which would barely hold the weight of a human, let alone an entire city." To combat this, they utilized timber piles from Croatia, driving them deep into the ground to create stable foundations. This method not only stabilized the structures but also improved the surrounding soil's strength by compressing it, effectively pushing out water.

As the city developed, the construction techniques evolved. Initially, wooden houses were built, but after experiencing numerous fires, the Venetians transitioned to brick. The narrator highlights the importance of flexibility in their construction, stating, "Lime mortar had to be used instead of cement because it was flexible and would allow the entire building to flex as the ground beneath slowly moved." This adaptability was crucial for the longevity of the structures, which still stand today.

The video also discusses the unique layout of Venice, which expanded inward rather than outward. The narrator notes, "Instead of expanding outwards like most cities, these islands expanded into each other," leading to a network of canals that facilitated transportation and trade. The absence of traditional roads allowed for a distinct separation of pedestrian and vehicular traffic, enhancing the city's efficiency.

As Venice grew, so did its population and the demand for fresh water. The narrator explains the innovative solutions the Venetians devised to collect rainwater, transforming squares into collection points. "Venice then became an enormous funnel, which filled more than 600 wells around the city," showcasing their resourcefulness in overcoming environmental challenges.

Waste management was another significant issue addressed in the video. The narrator describes the unsanitary conditions prior to the 16th century, where waste was often discarded into the streets. The introduction of underground tunnels to manage waste was a groundbreaking solution, allowing for a cleaner city. The narrator states, "The extremely salty water worked as a strong disinfectant, and thanks to this system, the streets became clean."

The video concludes by reflecting on the enduring legacy of Venetian engineering, with the narrator stating, "Amazingly, almost all of the incredible engineering that made Venice is still around today." This serves as a testament to the ingenuity and resilience of the Venetians, who transformed their challenging environment into one of the most iconic cities in the world. The video not only educates viewers about the historical and engineering aspects of Venice but also engages them with a narrative that highlights human creativity in the face of adversity.

Bias:
 The video presents a largely positive view of Venetian engineering and urban planning, emphasizing the ingenuity and resilience of its founders. While it highlights the challenges faced, it does not delve deeply into the socio-economic issues or the impact of such engineering on the local environment and communities. This could lead to a somewhat romanticized view of Venice's history, focusing primarily on its achievements without addressing potential downsides or criticisms of its development.

Exerpts:
- "The year is 452. The Roman Empire is on the brink of collapse, and the Huns have just launched their attack on Northern Italy."
- "Despite having no roads, no land, and no fresh water, the Venetians managed to turn a muddy swamp into the most powerful and wealthiest city of its time."
- "To create stable foundations for buildings, the Venetians collected large timber piles from the forests of Croatia and started hammering them into the ground."
- "This design was a stroke of genius, as the wooden piles were sealed away from the air, making it impossible for them to rot."
- "The next step in Venice's evolution would, of course, be connecting the islands."
- "Venice then became an enormous funnel, which filled more than 600 wells around the city."
- "The extremely salty water worked as a strong disinfectant, and thanks to this system, the streets became clean."
- "Amazingly, almost all of the incredible engineering that made Venice is still around today."
- "In order to turn Venice from a collection of islands into a bustling city, bridges had to be built."
- "The messy overlap of pedestrians and horse-drawn traffic didn't exist in Venice, since the walkways and canals were completely separated."

Interesting Counterpoints:
- The video does not address the environmental impact of building on marshy land, such as potential ecological disruption.
- It overlooks the social inequalities that may have existed in Venice, particularly regarding who benefited from the city's wealth and innovations.

Key Insights:
- Venice was built on marshy islands, requiring innovative engineering solutions.
- Timber piles were used to create stable foundations for buildings.
- The city expanded inward, utilizing canals instead of roads for transportation.
- Rainwater collection systems were developed to address the lack of fresh water.
- Underground tunnels were constructed for waste management, improving sanitation.

Sources used by author:
- Historical texts on Venice
- Engineering studies on Venetian construction
- Documentaries about the history of Venice

Full transcript and analysis: out_transcript.json
```

---

## Converting to a Command-Line Utility

I like to use this script as a command-line utility, which makes it that much easier to summarize videos. To do this:

1. Create a shell script named `digest` with the following content:

```bash
#!/bin/bash

VENV_PATH="/path/to/your/venv"
SCRIPT_PATH="/path/to/your/digest.py"

source "$VENV_PATH/bin/activate"
python3 "$SCRIPT_PATH" "$@"
deactivate
```

2. Make the script executable:

```bash
chmod +x digest
```

3. Move the script to a directory in your PATH:

```bash
sudo mv digest /usr/local/bin/
```

Now you can run the script from anywhere:

```bash
digest https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Remember to replace `/path/to/your/venv` and `/path/to/your/digest.py` with the actual paths on your system.