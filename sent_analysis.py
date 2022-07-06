import string
from dataclasses import dataclass
from collections import Counter
from nltk.corpus import stopwords
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


@dataclass()
class SentimentAnalyzer:
    emotions_file_path: str = "emotions.txt"
    sent_analyzer = SentimentIntensityAnalyzer()

    emotion_classes_list = []
    words_list = []
    with open(emotions_file_path, 'r') as file:
        for line in file:
            raw = line.replace("\n", '').replace(",", '').replace("'", '').strip().split(':')

            words_list.append(raw[0])
            emotion_classes_list.append(raw[1])

    emotions_raw = zip(words_list, emotion_classes_list)
    emotions_classes = set(emotion_classes_list)

    @staticmethod
    def clean_text(text: str):
        lower_case = text.lower()
        cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))

        return cleaned_text

    def analyze_sent(self, text: str):
        cleaned_text = self.clean_text(text)
        data = self.sent_analyzer.polarity_scores(cleaned_text)

        score = data['compound']
        sent_class = ""
        if score >= 0.05:
            sent_class = "pos"
        if -0.05 < score < 0.05:
            sent_class = "neu"
        if score <= -0.05:
            sent_class = "neg"

        return sent_class, score

    def get_emotion_info(self, text: str, lang="english"):
        cleaned_text = self.clean_text(text)

        tokenized_words = word_tokenize(cleaned_text, lang)

        final_words = []
        for word in tokenized_words:
            if word not in stopwords.words(lang):
                final_words.append(word)

        lemma_words = []
        for word in final_words:
            word = WordNetLemmatizer().lemmatize(word)
            lemma_words.append(word)

        text_emotion_list = []

        for word, emotion in self.emotions_raw:
            if word in lemma_words:
                text_emotion_list.append(emotion)

        emotions_counter_dict = dict.fromkeys(list(self.emotions_classes), 0)
        w = Counter(text_emotion_list)

        for key, val in w.items():
            if val > 0:
                emotions_counter_dict[key] = val
        return emotions_counter_dict


if __name__ == '__main__':
    sa = SentimentAnalyzer()
    print(sa.analyze_sent("i am happy"))
    print(sa.get_emotion_info("He is furious"))

