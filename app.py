from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from langdetect import detect
import matplotlib.pyplot as plt
import pyperclip
import streamlit as st
import spacy.cli
import spacy

st.title('Anonymize text with Presidio')

provider = NlpEngineProvider(conf_file="languages-config.yml")
nlp_engine_multi_language = provider.create_engine()

try:
    spacy.load("en_core_web_lg")
    spacy.load("it_core_news_lg")
    spacy.load("de_core_news_md")
    spacy.load("es_core_news_md")
    spacy.load("fr_core_news_sm")
except:
    spacy.cli.download("en_core_web_lg")
    spacy.cli.download("it_core_news_lg")
    spacy.cli.download("de_core_news_md")
    spacy.cli.download("es_core_news_md")
    spacy.cli.download("fr_core_news_sm")

presidio_supported_languages = ["en", "it"]

withAnalysis = st.toggle('Show analisys detail')
text = st.text_input('Text to anonymize')

if text:
    lang = detect(text)
    if lang not in presidio_supported_languages:
        st.error(f'Language not supported: {lang}')
        st.stop()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine_multi_language, supported_languages=presidio_supported_languages)
    anonymizer = AnonymizerEngine()
    analyzer_results = analyzer.analyze(text=text, language=lang)
    if analyzer_results:
        anonymized_results = anonymizer.anonymize(text=text, analyzer_results=analyzer_results)
        anonymize_result_text = anonymized_results.text
        for entity in analyzer_results:
            entity_plaholder = "#" * (entity.end - entity.start)
            anonymize_result_text = anonymize_result_text.replace(f"<{entity.entity_type}>", entity_plaholder)
        st.text_area("Anonymized text", anonymize_result_text)
        copy_button = st.button('Copy to clipboard')
        if copy_button:
            pyperclip.copy(anonymize_result_text)
            st.success('Copied to clipboard!', icon="✅")
        if withAnalysis:
            st.subheader('Analisys details')
            st.table({'type': entity.entity_type, 'from char': entity.start, 'to char': entity.end, 'score': entity.score, 'text': text[entity.start:entity.end]} for entity in analyzer_results)
            entities_type = [entity.entity_type for entity in analyzer_results]
            count_entities = {i:entities_type.count(i) for i in entities_type}
            plt.pie(count_entities.values(), labels=count_entities.keys(), autopct='%1.1f%%', shadow=False, startangle=20)
            plt.axis('equal')
            col1, col2 = st.columns(2)
            container = st.container()
            with container:
                with col1:
                    st.text('PII distribution')
                    col1.pyplot(plt)
                with col2:
                    st.text('PII count')
                    col2.bar_chart(count_entities)
    else:
        st.info('No PII found in text', icon="ℹ️")