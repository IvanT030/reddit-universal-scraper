import torch
from typing import List, Tuple

class StanceAnalyzer:

    def __init__(self):
        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
            logging as transformers_logging
        )

        transformers_logging.set_verbosity_error()

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model_name = (
            "Qwen/Qwen3-4B-Instruct-2507"
        )

        print("Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        print("Loading model...")

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )

        self.model.eval()

        self.valid_labels = [
            "agree",
            "disagree",
            "discussion",
            "not related"
        ]

    def build_prompt(
        self,
        text1: str,
        text2: str
    ) -> str:

        return f"""
        You are a stance detection system.
        Determine the relationship between the premise and the hypothesis.
        Labels:
        agree
        - supports or agrees with the premise
        disagree
        - opposes or rejects the premise
        discussion
        - discusses the topic, gives opinions, asks questions,
        gives suggestions, or elaborates without clear agreement or disagreement
        not related
        - irrelevant, meaningless, or unrelated to the premise
        Rules:
        - Choose ONLY ONE label
        - Output ONLY the label
        - Do not explain
        Premise:
        {text1}
        Hypothesis:
        {text2}
        Label:
        """

    def clean_prediction(
        self,
        prediction: str
    ) -> str:

        prediction = prediction.lower().strip()

        if "agree" in prediction and "disagree" not in prediction:
            return "agree"

        if "disagree" in prediction or "contradiction" in prediction:
            return "disagree"

        if (
            "discussion" in prediction
            or "suggestion" in prediction
            or "discuss" in prediction
        ):
            return "discussion"

        if (
            "not related" in prediction
            or "unrelated" in prediction
            or "irrelevant" in prediction
        ):
            return "not related"

        return "discussion"

    def analyze_stance(
        self,
        text1: str,
        text2: str
    ) -> str:

        if not text1 or not text2:
            return "not related"

        prompt = self.build_prompt(
            text1,
            text2
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(self.device)

        with torch.no_grad():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=10,
                do_sample=False
            )

        generated_tokens = outputs[0][
            inputs["input_ids"].shape[1]:
        ]

        prediction = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        ).strip()

        print(prediction, self.clean_prediction(prediction))

        return self.clean_prediction(
            prediction
        )

    def analyze_batch(
        self,
        pairs: List[Tuple[str, str]]
    ) -> List[str]:

        results = []

        for text1, text2 in pairs:

            result = self.analyze_stance(
                text1,
                text2
            )

            results.append(result)

        return results


class _LazyAnalyzer:
    def __init__(self):
        self._instance = None

    def _load(self):
        if self._instance is None:
            self._instance = StanceAnalyzer()
        return self._instance

    def __getattr__(self, name):
        return getattr(self._load(), name)


analyzer = _LazyAnalyzer()

def analyze_stance(
    text1: str,
    text2: str
) -> str:

    return analyzer.analyze_stance(
        text1,
        text2
    )


def analyze_batch(
    pairs: List[Tuple[str, str]]
) -> List[str]:

    return analyzer.analyze_batch(
        pairs
    )


if __name__ == "__main__":

    test_pairs = [

        (
            "I keep seeing pro players and coaches say that the phantom / vandal are better than the other, I’d like opinions from actual players instead. If you prefer one gun over the other, please share why!?",
            "Phantom is better for smoke checks since it doesnt leave direct trail of your fire to find you easily. Vandal is better for headshot killing."
        ),

        (
            "I keep seeing pro players and coaches say that the phantom / vandal are better than the other, I’d like opinions from actual players instead. If you prefer one gun over the other, please share why?",
            "i dont think it matters anymore, maybe the phantom is slightly better?"
        ),

        (
            "I keep seeing pro players and coaches say that the phantom / vandal are better than the other, I’d like opinions from actual players instead. If you prefer one gun over the other, please share why?",
            "This might sound odd but I prefer the Phantom on defense and Vandal on attack. I'd say majority of my fights on the defense side are typically medium/short range (I usually play more support agents an"
        ),

        (
            "I keep seeing pro players and coaches say that the phantom / vandal are better than the other, I’d like opinions from actual players instead. If you prefer one gun over the other, please share why!",
            "Phantom is objectively better, so if you have to choose one, go for phantom. \
            In some cases vandal is preferred. Some use cases for the Vandal are: \
            making a ton of noise to put pressure"
        ),
    ]

    results = analyze_batch(
        test_pairs
    )

    for pair, result in zip(
        test_pairs,
        results
    ):

        print(
            f"{pair[0][:30]}... vs "
            f"{pair[1][:30]}... -> {result}"
        )