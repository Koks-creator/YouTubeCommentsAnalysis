from time import perf_counter
import pandas as pd
from autocorrect import Speller
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


from sent_analysis import SentimentAnalyzer
from youtube_comments import YouTubeComments

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

start = perf_counter()
sentiment_analyzer = SentimentAnalyzer()
yt_comms = YouTubeComments()
spell = Speller(lang='en')

url = "https://www.youtube.com/watch?v=wq9YWV_vycs"
comments_dict = yt_comms.get_comments(video_url=url, max_results=200)
title, likes, views = yt_comms.get_video_basic_info(video_url=url)

df = pd.DataFrame.from_dict(comments_dict)
df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

# outcomment this line if you aim for a little bit of better accuracy with vader but much longer time of execution
# df['Comments'] = df['Comments'].apply(lambda x: spell(x))

# nakladanie funkcji na komentarze za datasetu i zamienianie na liste
analyzed_sents_list = df['Comments'].apply(lambda x: sentiment_analyzer.analyze_sent(x)).to_list()
sent_emotions_list = df['Comments'].apply(lambda x: sentiment_analyzer.get_emotion_info(x)).to_list()

# rozdzielanie na punkty i klase
classes_list = []
points_list = []
for analyzed_sent in analyzed_sents_list:
    classes_list.append(analyzed_sent[0])
    points_list.append(analyzed_sent[1])

# tworzenie kolumn
df['Class'] = classes_list
df['Points'] = points_list

# sent_emotions_list to lista slownikow, z tego robimy nowy dataset i laczymy ze starym
emotions_df = pd.DataFrame.from_records(sent_emotions_list)
final_df = pd.concat([df, emotions_df], axis=1, join='inner')

# liczenie ile razy powtorzyly sie dane emocje

print()
for col in emotions_df.columns:
    num = len(emotions_df[col][emotions_df[col] > 0])
    print(f"{col}: {num}")


print("Negative comments:")
print(df[['Comments', 'Class', 'Points', 'Likes']][df['Class'] == "neg"])

print("Positive comments:")
print(df[['Comments', 'Class', 'Points', 'Likes']][df['Class'] == "pos"])


def colors_list(points_list: list) -> list:
    colors = []
    for points in points_list:
        if points >= 0.05:
            colors.append("green")
        if -0.05 < points < 0.05:
            colors.append("blue")
        if points <= -0.05:
            colors.append("red")

    return colors


colors_for_pieplot = {
    df['Class'][df['Class'] == "neu"].count(): "neu",
    df['Class'][df['Class'] == "neg"].count(): "neg",
    df['Class'][df['Class'] == "pos"].count(): "pos",
}
keys = list(colors_for_pieplot.keys())
keys.sort(reverse=True)
final_pie_colors = [colors_for_pieplot[key] for key in keys]

fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 2]}, figsize=(15, 5))

ax1.pie(df['Class'].value_counts(), autopct=lambda p: '{:.2f}%({:.0f})'.format(p, (p/100)*df.groupby('Comments').size().sum()))
ax1.legend(final_pie_colors, loc="best")

ax2.scatter(df['Date'], df['Points'], marker='o', c=colors_list(points_list))

green_patch = mpatches.Patch(color='green', label='Pos')
blue_patch = mpatches.Patch(color='blue', label='Neu')
red_patch = mpatches.Patch(color='red', label='Neg')

ax2.legend(handles=[green_patch, blue_patch, red_patch], loc="best")
plt.gcf().autofmt_xdate()
# fig.tight_layout()

plt.title(f"{title} ({views} views, {likes} likes)", loc='right')

end = perf_counter()
print(end - start)
plt.show()


