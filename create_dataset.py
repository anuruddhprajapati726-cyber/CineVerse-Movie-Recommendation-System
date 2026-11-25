import pandas as pd

rows = [
    # HOLLYWOOD
    (
        1001,
        "Dune: Part Two",
        "Hollywood",
        "Science Fiction, Adventure",
        (
            "Paul Atreides unites with Chani and the Fremen while seeking"
            " revenge against the conspirators who destroyed his family."
        ),
        (
            "science fiction adventure desert sandworm arrakis paul atreides"
            " sequel epic"
        ),
    ),
    (
        1002,
        "Oppenheimer",
        "Hollywood",
        "Drama, History",
        (
            "The story of American scientist J. Robert Oppenheimer and his role"
            " in the development of the atomic bomb."
        ),
        "drama history biography physics scientist world war ii",
    ),
    (
        1003,
        "Deadpool & Wolverine",
        "Hollywood",
        "Action, Comedy, Science Fiction",
        (
            "Deadpool is offered a place in the Marvel Cinematic Universe by"
            " the Time Variance Authority, recruiting Wolverine to save his"
            " universe."
        ),
        "action comedy superhero marvel multiverse wolverine",
    ),
    (
        1004,
        "Inside Out 2",
        "Hollywood",
        "Animation, Family, Comedy",
        (
            "Teenager Riley's mind headquarters undergoes a sudden demolition to"
            " make room for new emotions like Anxiety."
        ),
        "animation family comedy emotions pixar teenage",
    ),
    (
        1005,
        "Interstellar",
        "Hollywood",
        "Adventure, Drama, Science Fiction",
        (
            "A team of explorers travel through a wormhole in space in an"
            " attempt to ensure humanity's survival."
        ),
        "space wormhole time dilation astronaut survival drama",
    ),
    (
        1006,
        "Inception",
        "Hollywood",
        "Action, Science Fiction, Adventure",
        (
            "A thief who steals corporate secrets through dream-sharing"
            " technology is given the inverse task of planting an idea."
        ),
        "dreams subconscious heist mind bending thriller",
    ),
    (
        1007,
        "The Dark Knight",
        "Hollywood",
        "Drama, Action, Crime",
        (
            "Batman raises the stakes in his war on crime against the Joker in"
            " Gotham City."
        ),
        "superhero batman joker gotham crime thriller",
    ),
    (
        1008,
        "Avatar: The Way of Water",
        "Hollywood",
        "Science Fiction, Adventure, Action",
        (
            "Jake Sully lives with his newfound family formed on the extrasolar"
            " moon Pandora."
        ),
        "pandora ocean alien sci-fi family adventure",
    ),
    (
        1009,
        "John Wick: Chapter 4",
        "Hollywood",
        "Action, Thriller, Crime",
        (
            "John Wick uncovers a path to defeating The High Table while facing"
            " a new enemy with powerful alliances."
        ),
        "assassin martial arts gun fu revenge thriller",
    ),
    (
        1010,
        "Top Gun: Maverick",
        "Hollywood",
        "Action, Drama",
        (
            "After thirty years, Maverick is still pushing the envelope as a top"
            " naval aviator while training a detachment of graduates."
        ),
        "fighter jet aviation navy pilot action drama",
    ),
    # BOLLYWOOD
    (
        2001,
        "Jawan",
        "Bollywood",
        "Action, Thriller",
        (
            "A high-octane action thriller which outlines the emotional journey"
            " of a man who is set to rectify the wrongs in society."
        ),
        "action thriller vigilante social justice mass entertainer",
    ),
    (
        2002,
        "Pathaan",
        "Bollywood",
        "Action, Thriller, Adventure",
        (
            "An Indian spy takes on the leader of a group of mercenaries who"
            " have nefarious plans to target his homeland."
        ),
        "spy universe espionage action thriller raw agent",
    ),
    (
        2003,
        "Animal",
        "Bollywood",
        "Action, Crime, Drama",
        (
            "A hardened son's obsessive love for his father leads him down a"
            " dark and violent path of revenge."
        ),
        "crime drama family revenge intense action",
    ),
    (
        2004,
        "12th Fail",
        "Bollywood",
        "Drama, Biography",
        (
            "Based on the true story of IPS officer Manoj Kumar Sharma who"
            " fearlessly embraced the idea of restarting his academic journey."
        ),
        "biography upsc motivation struggle inspiration drama",
    ),
    (
        2005,
        "Stree 2",
        "Bollywood",
        "Horror, Comedy",
        (
            "After the events of Stree, the town of Chanderi is being haunted"
            " again, this time by a headless entity called Sarkata."
        ),
        "horror comedy folklore small town mystery",
    ),
    (
        2006,
        "Kalki 2898 AD",
        "Bollywood",
        "Science Fiction, Action, Fantasy",
        (
            "A modern-day avatar of Vishnu descends to Earth to protect the"
            " world from evil forces in a dystopian future."
        ),
        "mythology sci-fi dystopian future action epic",
    ),
    (
        2007,
        "Fighter",
        "Bollywood",
        "Action, Thriller",
        (
            "Top IAF aviators come together in the face of imminent danger to"
            " form Air Dragons."
        ),
        "indian air force fighter jet patriotism aerial action",
    ),
    (
        2008,
        "3 Idiots",
        "Bollywood",
        "Comedy, Drama",
        (
            "Two friends are searching for their long lost companion while"
            " revisiting their college days and inspiring memories."
        ),
        "college friendship education comedy drama",
    ),
    (
        2009,
        "Dangal",
        "Bollywood",
        "Drama, Family, Biography",
        (
            "Former wrestler Mahavir Singh Phogat trains his daughters Geeta and"
            " Babita to become India's first world-class female wrestlers."
        ),
        "wrestling sports biography empowerment family drama",
    ),
    (
        2010,
        "Brahmāstra: Part One – Shiva",
        "Bollywood",
        "Fantasy, Action, Adventure",
        (
            "A DJ with superpowers and his ladylove embark on a journey to"
            " protect the Brahmastra, a weapon of enormous energy."
        ),
        "astraverse mythology fantasy superpowers adventure",
    ),
    # ANIME
    (
        3001,
        "Your Name",
        "Anime",
        "Animation, Romance, Fantasy",
        (
            "Two teenagers share a profound, magical connection upon discovering"
            " they are swapping bodies."
        ),
        "body swap romance fantasy comet time makoto shinkai",
    ),
    (
        3002,
        "Spirited Away",
        "Anime",
        "Animation, Family, Fantasy",
        (
            "During her family's move to the suburbs, a sullen 10-year-old girl"
            " wanders into a world ruled by gods, witches, and spirits."
        ),
        "studio ghibli spirits fantasy adventure magic",
    ),
    (
        3003,
        "Demon Slayer: Mugen Train",
        "Anime",
        "Animation, Action, Fantasy",
        (
            "Tanjiro Kamado and his friends board the Mugen Train to"
            " investigate a mysterious series of disappearances alongside the"
            " Flame Hashira."
        ),
        "demon slayer swordsmanship hashira action fantasy",
    ),
    (
        3004,
        "Jujutsu Kaisen 0",
        "Anime",
        "Animation, Action, Fantasy",
        (
            "Yuta Okkotsu gains control of an extremely powerful cursed spirit"
            " and gets enrolled in the Tokyo Prefectural Jujutsu High School."
        ),
        "curses sorcerer action dark fantasy anime",
    ),
    (
        3005,
        "Suzume",
        "Anime",
        "Animation, Adventure, Fantasy",
        (
            "A modern action adventure road story where a 17-year-old girl"
            " helps a mysterious young man close doors from the other side that"
            " are releasing disasters."
        ),
        "doors disaster road trip fantasy makoto shinkai",
    ),
    (
        3006,
        "A Silent Voice",
        "Anime",
        "Animation, Drama, Romance",
        (
            "A young man is ostracized by his classmates after he bullies a deaf"
            " girl to the point where she moves away, seeking redemption years"
            " later."
        ),
        "redemption school drama emotional friendship",
    ),
    (
        3007,
        "Attack on Titan: The Last Attack",
        "Anime",
        "Animation, Action, Drama",
        (
            "Humanity fights for survival against giant man-eating Titans as"
            " the Rumbling threatens to destroy the world."
        ),
        "titans survival dark fantasy war action",
    ),
    (
        3008,
        "One Piece Film: Red",
        "Anime",
        "Animation, Adventure, Music",
        (
            "Uta, the most beloved singer in the world, reveals herself to the"
            " world at a live concert where Luffy and the Straw Hats attend."
        ),
        "pirates music adventure luffy shanks",
    ),
    (
        3009,
        "Weathering With You",
        "Anime",
        "Animation, Drama, Fantasy",
        (
            "A high-school boy who has run away to Tokyo befriends a girl who"
            " appears to be able to manipulate the weather."
        ),
        "rain weather tokyo romance fantasy",
    ),
    (
        3010,
        "Dragon Ball Super: Super Hero",
        "Anime",
        "Animation, Action, Science Fiction",
        (
            "The Red Ribbon Army from Goku's past has returned with two new"
            " androids to challenge Gohan and Piccolo."
        ),
        "saiyan martial arts androids action power",
    ),
]

df = pd.DataFrame(
    rows, columns=["movie_id", "title", "category", "genres", "overview", "tags"]
)
df["combined_tags"] = (
    df["category"]
    + " "
    + df["genres"]
    + " "
    + df["overview"]
    + " "
    + df["tags"]
).str.lower()
df.to_csv("latest_movies_dataset.csv", index=False)
print("Done! Created latest_movies_dataset.csv with", len(df), "movies.")