from sentence_transformers import CrossEncoder
from typing import List, Tuple

class DebertaAnalyzer:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/nli-deberta-v3-base')

        self.label_mapping = [
            'contradiction',
            'entailment',
            'neutral'
        ]

    def analyze_stance(self, text1: str, text2: str) -> str:
        """分析單個文本對的立場"""

        if not text1 or not text2:
            return 'neutral'

        scores = self.model.predict([(text1, text2)])

        label_idx = scores.argmax(axis=1)[0]

        return self.label_mapping[label_idx]

    def analyze_batch(
        self,
        pairs: List[Tuple[str, str]]
    ) -> List[str]:
        """批量分析文本對"""

        if not pairs:
            return []

        valid_pairs = []

        for t1, t2 in pairs:

            t1_str = str(t1) if t1 is not None else ''
            t2_str = str(t2) if t2 is not None else ''

            if t1_str.strip() and t2_str.strip():
                valid_pairs.append((t1_str, t2_str))

        if not valid_pairs:
            return ['neutral'] * len(pairs)

        scores = self.model.predict(valid_pairs)

        labels = [
            self.label_mapping[score.argmax()]
            for score in scores
        ]

        result = []

        valid_idx = 0

        for t1, t2 in pairs:

            t1_str = str(t1) if t1 is not None else ''
            t2_str = str(t2) if t2 is not None else ''

            if t1_str.strip() and t2_str.strip():

                result.append(labels[valid_idx])

                valid_idx += 1

            else:
                result.append('neutral')

        return result

# 全局實例
analyzer = DebertaAnalyzer()
def analyze_stance(text1: str, text2: str) -> str:
    return analyzer.analyze_stance(text1, text2)

def analyze_batch(
    pairs: List[Tuple[str, str]]
) -> List[str]:

    return analyzer.analyze_batch(pairs)

if __name__ == "__main__":
    test_pairs = [

        (
            "Valorant is a great game",
            "Valorant is terrible"
        ),

        (
            "I love this character",
            "I love this character"
        ),

        (
            "The patch is broken",
            "The patch is fine"
        ),

        (
            "AI will replace programmers",
            "I completely agree"
        ),

    ]

    results = analyze_batch(test_pairs)
    for pair, result in zip(test_pairs, results):

        print(
            f"{pair[0][:30]}... vs "
            f"{pair[1][:30]}... -> {result}"
        )