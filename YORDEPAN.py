import streamlit as st
import pandas as pd
from functools import reduce
from datetime import datetime
import string
from time import sleep
from conllu import parse
from streamlit.errors import StreamlitValueAboveMaxError as SVAME

UPOS = {'ADJ':'ADJECTIVE',
         'ADP':'ADPOSITION', 
         'ADV':'ADVERB', 
         'AUX':'AUXILLIARY', 
         'CCONJ':'COORDIANTING CONJUNCTION', 
         'DET':'DETERMINER', 
         'INTJ':'INTERJECTION', 
         'NOUN':'NOUN', 
         'NUM':'NUMBER', 
         'PART':'PARTICIPLE', 
         'PRON':'PRONOUN', 
         'PROPN':'PROPER NOUN', 
         'PUNCT':'PUNCTUATION', 
         'SCONJ':'SUBORDINATING CONJUCTION', 
         'SYM':'SYMBOL', 
         'VERB':'VERB', 
         'X':'UNDEFINED - PLEASE INDICATE THE APPROPRIATE POS TAG IN THE XPOS INPUT BOX'}
DEPREL = {'acl':'clausal modifier of noun (adnominal clause)',
                    'acl:relcl':'relative clause modifier',
                    'advcl':'adverbial clause modifier',
                    'advcl:relcl':'adverbial relative clause modifier',
                    'advmod':'adverbial modifier',
                    'advmod:emph':'emphasizing word, intensifier',
                    'advmod:lmod':'locative adverbial modifier',
                    'amod':'adjectival modifier',
                    'appos':'appositional modifier',
                    'aux':'auxilliary',
                    'aux:pass':'passive auxilliary',
                    'case':'case marking',
                    'cc':'coordinating conjunction',
                    'cc:preconj':'preconjuction',
                    'ccomp':'clausal complement',
                    'clf':'classifier',
                    'compound':'compound',
                    'compound:lvc':'light verb construction',
                    'compound:prt':'phrasal verb particle',
                    'compound:redup':'reduplicated compounds',
                    'compound:svc':'serial verb compounds',
                    'conj':'conjunct',
                    'cop':'copula',
                    'csubj':'clasual subject',
                    'csubj:outer':'outer clause clausal subject',
                    'csubj:pass':'clausal passive subject',
                    'dep':'unknown dependency',
                    'det:nomgov':'pronominal quantifier governing the case of the noun',
                    'det:nummod':'pronominal quantifier agreeing in case with the noun',
                    'det:poss':'possessive determiner',
                    'discourse':'discourse element',
                    'dislocated':'dislocated element',
                    'expl':'expletive',
                    'expl:impers':'impersonal expletive',
                    'expl:pass':'reflexive pronoun used in reflexive passive',
                    'expl:pv':'reflexive clitic with an inherently reflexive verb',
                    'foc':'focus marker',
                    'fixed':'fixed multiword expression',
                    'flat':'flat expression',
                    'flat:foreign':'foreign words',
                    'flat:name':'names',
                    'goeswith':'goes with',
                    'iobj':'indirect object',
                    'list':'list',
                    'mark':'marker',
                    'nmod':'nominal modifier',
                    'nmod:poss':'possessive nominal modifier',
                    'nmod:tmod':'temporal modifier',
                    'nsubj':'nominal subject',
                    'nsubj:outer':'outer clause nominal subject',
                    'nsubj:pass':'passive nominal subject',
                    'nummod':'numeric modifier',
                    'nummod:gov':'numeric modifier governing the case of the noun',
                    'obj':'object',
                    'obl':'oblique nominal',
                    'obl:agent':'oblique agent in passive construction',
                    'obl:arg':'oblique argument',
                    'obl:lmod':'locative modifier',
                    'obl:tmod':'temporal modifier',
                    'orphan':'orphan',
                    'parataxis':'parataxis',
                    'punct':'punctuation',
                    'reparandum':'overriden disfluency',
                    'root':'root',
                    'vocative':'vocative',
                    'xcomp':'open clausal complement'}

def tokenize(text:str):
    letters = [char for char in text]
    new = []
    for char in letters:
        if char not in list(string.punctuation+'£¢©¥≤ϵ≥™≠ꓯ÷®₦№℗'):
            new.append(char)
        else:
            new.extend([' ',char,' '])
    tokens = reduce(lambda x,y:x+y, new)
    for i in tokens.split(' ')[:-1]:
        yield(i)

def intro():
    st.subheader('THIS IS A WEBAPP TO ANNOTATE THE TOKENS PER SENTENCE IN A SEMI-AUTOMATIC MANNER FOR A DEPENDENCY PARSE TREE. THE RESULT CAN BE DOWNLOADED AS .TXT OR .CONLLU FORMAT FOR FURTHER CLEANING, ANALYSIS OR TREEBANK CREATION.')
    '___'
    st.write('AT THE SIDEBAR ON THE LEFT OF YOUR SCREEN, `CHOOSE AN ACTION HERE`, click the `arrow down`, then click `ANNOTATE` to start annotating your sentences. Or read below information, then annotate afterwards.')
    st.write('If you cannot see the `CHOOSE AN ACTION HERE`, kindly click the `>>` at the top-left corner of your screen and follow the prompt.')
    st.write('$THANK$ $YOU$ $AND$ $GOODLUCK!$')
    '___'
    with st.expander('`🤔💭 WHAT IS THIS ABOUT?`'):
        st.markdown('''\n
                The dependency parsing is one of the many approaches to answering the question: `HOW CAN A MACHINE UNDERSTAND THE SYNTAX OF A LANGUAGE?` This approach seeks to present a language's syntax as a `dependency tree` with individual tokens as `nodes` and their syntactic relationship among one another as `edges` (Mark-Jan Nederhof & Giorgio Satta, 2010:120).
                With a language's syntax now represented as a dependency tree, a machine can understand how each words relates to one another in a sentence and can achieve tasks like translation from one language to another, or even communicate to us like a human!
                This annotation scheme is based on the fact that **every word in a sentence shares a relationship with another, either as a head or as a dependent**. The result of this scheme is a `dependency treebank` which allows the machine to focus and understand the relation between a head and its dependent by representing sentences as a dependecy tree (Martha Palmer & Nianwen Xue, 2010:242).
                Tokens of sentences are tagged in the format that have been universally agreed in the (UD) Universal Dependencies - a project that has successfully provided a universal
                inventory of categories/tagsets to facilitate a concise cross-linguistic grammar formalism and easy comprehension by experts and non-specialists involved in this community-wide involvement (O̩lájídé Ìshò̩lá & Daniel Zeman, 2020). This format is named the CoNNL-U format, it highlights ten features per tokens in a document/sentence.
                They include:
                * **ID**: This is the index of an individual token in a document/sentence. The index of a token is usually `{x | x ϵ N and x ≤ len(sentence.split(' '))}`. Or simply put, the ID of a token:
                    * must be a member of the set of Natural numbers.
                    * must be lesser than the total amount of tokens in the sentence you want to annotate. **Please note that the punctuations are also regarded as a token.**
                * **FORM**: This is usually the surface level representation of the token selected for annotation - as it is in the sentence. 
                * **LEMMA**: This is the root form of the token selected. The lemma of a token is usually the dictionary form of the token selected. For example, the lemma of the token `running` is `run`.
                * **UPOS**: This is the universally accepted Part-Of-Speech tag for the token selected. It is usually one of the provided 17 tags.
                * **XPOS**: This is the language specific Part-Of-Speech tag for the token selected. If unknown, leave as `_`.
                * **FEATS**: This is usually a list of morphological features of the token selected. It is usually written as **Attribute=Value** or -as in the case of two or more features- **Attribute=Value | Attribute=Value | Attribute=Value | etc...** E.g: `We` will be tagged as `Number=Plur|Person=1`.
                * **HEAD**: This is usually the ID of the syntactic head (that is, the ID of the word that the selected token depends on). It is usually an integer and MUST be `0` if the `deprel` of the selected token is a `root`! Mathematically put, `x=0 iff deprel(token)==root`.
                * **DEPREL**: This is usually the type of relation a token has to its syntactic head. It is usually one of the options provided in the app.
                * **DEPS**: This is the extra dependency information. It is usually any other dependency that the selected token shares with another token and is usually represented as `HEAD:DEPREL` or as is the case of two or more "deps", we represent as `HEAD:DEPREL | HEAD:DEPREL`. This option can also be left as `_` if there is nothing.
                * **MISC**: This is for any other information about the token selected for annotation. E.g `SpaceAfter=No` or `Typo=Yes` or `SpaceAfter=No | Typo=Yes`. You may also choose to leave this field at its default value of `_`.            
                ''')
        '___'
        tab1, tab2, tab3 = st.tabs(['A LIST OF AVAILABLE UPOS', 'A LIST OF AVAILABLE DEPREL TAGS', 'A BRIEF DESCRIPTION OF FEATS'])
        with tab1:
            st.write('YOU CAN ONLY CHOOSE ONE OF THESE PARTS OF SPEECH FOR A TOKEN\'S UPOS. THESE ARE THE TAGS UNIVERSALLY AGREED FOR ALL LANGUAGES. HOWEVER, **LANGUAGE SPECIFIC POS SHOULD BE INDICATED IN THE XPOS BOX**.')
            with st.expander('SEE UPOS TAGS HERE: INFORMATION IS DISPLAYED AS: `<TAG>`:`<DESCRIPTION>`'):
                for i,j in UPOS.items():
                    st.write(f'`{i}`:`{j}`')
        
        with tab2:
            st.write('YOU CAN ONLY CHOOSE ONE OF THESE TAGS TO REPRESENT A TOKEN\'S RELATIONSHIP TO ITS SYNTACTIC HEAD. THESE TAGS WERE SOURCED FROM `https://universaldependencies.org/u/dep/index.html`')
            with st.expander('CLICK TO SEE DEPENDENCIES AND THIER DESCRIPTION. INFO IS DIESPLAYED AS: `<TAG>`:`<DESCRIPTION>`'):
                for i, j in DEPREL.items():
                    st.write(f'`{i}`:`{j}`')
    
        with tab3:
            st.write('THIS REPRESENTS THE FEATURES OF THE TOKEN SELECTED FOR TAGGING. PLEASE LEAVE AT THE DEFAULT VALUE `_` IF YOU ARE NOT SURE OF THE FEATURES POSSESSED BY THE TOKEN. MULTIPLE FEATURES (`FEATS`) ARE DELIMITED WITH A `|`.' \
            'E.G The token `I` may be tagged as `Person=1|Number=Sing` or `Person=1` or `Number=Sing`.')
            with st.expander('CLICK HERE TO SEE THE LIST OF POPULAR FEATURES. INFO IS DISPLAYED AS `<FEATURE>`=`<VALUE>` `(MEANING OF VALUE)`'):
                st.write('**THESE ARE NOT THE ONLY FEATURES AVAILABLE, BUT THE MOST FREQUENTLY ENCOUNTERED**')
                st.markdown("""
                            * `Case`=`Nom` `(Nominative)`
                            * `Case`=`Acc` `(Accusative)`
                            * `Case`=`Gen` `(Genitive)`
                            * `Case`=`Dat` `(Dative)`
                            * `Gender`=`Masc` `(Masculine)`
                            * `Gender`=`Fem` `(Feminine)`
                            * `Gender`=`Neut` `(Neuter)`
                            * `Number`=`Sing` `(Singular)`
                            * `Number`=`Plur` `(Plural)`
                            * `Tense`=`Past` `(Past Tense)`
                            * `Tense`=`Pres` `(Present Tense)`
                            * `Tense`=`Fut` `(Future Tense)`
                            * `Tense`=`Non-Fut` `(Non-Future Tense)`
                            * `Mood`=`Ind` `(Indicative)`
                            * `Mood`=`Imp` `(Imperative)`
                            * `Mood`=`Sub` `(Subjunctive)`
                            * `Person`=`1` `(First person)`
                            * `Person`=`2` `(Second person)`
                            * `Person`=`3` `(Third person)`
                            * `Voice`=`Act` `(Active voice)`
                            * `Voice`=`Pass` `(Passive voice)`
                            * `Aspect`=`Perf` `(Perfect)`
                            * `Aspect`=`Imp` `(Imperfect)`
                            * `Degree`=`Pos` `(Positive)`
                            * `Degree`=`Cmp` `(Comparative)`
                            * `Degree`=`Sup` `(Superlative)`
                            * `Definite`=`Def` `(Definite)`
                            * `Definite`=`Ind` `(Indefinite)`
                            * `Definite`=`Def` `(Definite)`
                            * `VerbType`=`Trans` `(Transitive)`
                            * `VerbType`=`Intr` `(Intransitive)`
""")
    
        with st.expander('📚📖 REFERENCES AND FURTHER READINGS:'):
            st.markdown(
                """
                * https://universaldependencies.org
                * O̩lájídé Ìshò̩lá & Daniel Zeman (2020), Yorùbá Dependency Treebank (YTB). _Proceedings of the 12th Conference on Language
                 Resources and Evaluation (LREC 2020), 5178-5186_.
                * Mark-Jan Nederhof & Giorgio Satta (2010), Theory of Parsing. _The Handbook of Computational Linguistics and Natural
                 Language Processing_ 4(6):120-123.
                * Martha Palmer & Nianwen Xue (2010), Linguistic Annotation. _The Handbook of Computational Linguistics and Natural Language
                 Processing_ 10:242-244.
                """
            )
    
    with st.expander('COURTESY OF:', icon='✉'):
        st.markdown("""
                * **THE UNIVERSITY OF IBADAN**
                * Post Graduate Department of Computational Linguistics (2024/2025)
                * Project undertaken by: Kó̩láwo̩lé Olúrántí Lawal (246389)
                """)

def annotate():
    with st.sidebar:
        st.write('You will be recognized in this effort, if only we know how to address you. You may choose to remain anonymous while tagging though.')
        anon = st.toggle('Turn off to be anonymous', value=True)
        if anon == False:
            if 'USER' in st.session_state:
                del st.session_state.USER
                user = '🥷🏽'
                st.toast(f'Welcome {user}')
                st.write('Hello 👋🏾🥷🏽. You are anonymous.')
        else: 
            user = st.text_input('ENTER NAME HERE.')
            register = st.button('REGISTER')
            if register:
                if user:
                    if 'USER' not in st.session_state:
                        user = st.session_state.USER = user
                        st.toast(f'Welcome {st.session_state.USER}')
                    else:
                        del st.session_state.USER
                        st.session_state.USER = user

    st.write(f'**Hello {st.session_state.USER if 'USER' in st.session_state else '🥷🏽'},** DO NOT LEAVE THIS PAGE WHILE ANNOTATING TO AVOID THE RISK OF LOOSING YOUR DATA!')
    file_bool = st.toggle('DO YOU WANT TO ADD TO EXISTING FILE(S)?'.capitalize())
    if file_bool:
        files = st.file_uploader('ONLY .txt and .conllu files ARE ALLOWED!', type = ['conllu', 'txt'], accept_multiple_files=True)
        process = st.button('PROCESS')
        if process:
            if files:
                try:
                    for file in files:
                        content = file.getvalue().decode(encoding = 'utf-8')
                        try:
                            sent = parse(content)
                            if 'CONLLU' not in st.session_state:
                                st.session_state.CONLLU = content
                            else:
                                st.session_state.CONLLU+= content
                        except:
                            st.toast(f'COULDN\'T PARSE {file.name}')

                except:
                    st.toast('YOUR FILE COULD NOT BE PARSED! CHECK FILE AND TRY AGAIN.')
    '___'
    tokens = []
    text = st.text_area('**INPUT TEXT HERE:**', placeholder='PLEASE ONLY INPUT ONE SENTENCE HERE. IT MAY BE SIMPLE, COMPOUND, COMPLEX OR COMPOUND-COMPLEX.')
    button = st.button('ANNOTATE')
    col1, col2 = st.columns(2)
    if button:
        if not text:
            st.subheader('There is nothing to annotate!'.upper())  
    try:       
        tokens = [token for token in list(tokenize(text)) if token]
        with col1.expander('SEE TOKEN(S) AND THEIR ID HERE.'):
            for i, j in enumerate(tokens if len(text.split(' ')) > 1 else text.split(' '), 1):
                st.write(f'`{i}` `{j}`')
    except:
        pass

    form = col2.selectbox('SELECT WORD TO TAG HERE', options = tokens if len(text.split(' '))>1 else text)

    with st.form(key='form', clear_on_submit=False, enter_to_submit=False, border=False):
        if not text and 'DATA' in st.session_state:
            del st.session_state.DATA

        col1, col2, col3 = st.columns(3)
        col2.metric('TOKEN SELECTED:', value=form, border = True, width = 'content')
        try:
            id = st.number_input('SELECT ID HERE', min_value=1, max_value=len(tokens))
        except SVAME:
            id = st.number_input('SELECT ID HERE:', min_value=0, max_value=0)
        col1, col2, col3 = st.columns(3)
        lemma = col1.text_input('ENTER LEMMA HERE', value = form.lower() if form else None)
        upos = col2.selectbox('SELECT UNIVERSAL PART OF SPEECH HERE:', options = UPOS, index = 0)
        xpos = col3.text_input('INPUT XPOS TAG HERE', value = '_')
        
        col1, col2, col3 = st.columns(3)
        feat = col1.text_input('INPUT FEAT HERE:', value = '_')
        head = col2.number_input('HEAD', min_value = 0, max_value=len(tokens))
        deprel = col3.selectbox('SELECT DEPENDENCY HERE:', options = DEPREL.keys())       
        deps = st.text_input('INPUT SECONDARY DEPENDENCY HERE:',
                             help='Enhanced dependency graph in the form of a list of head-deprel pairs. Please separate multiple dependencies with a |. For example; ***0 : acl | 3 : nsubj | 0 : csubj***',
                             value = '_')
        misc = st.text_input('ANY OTHER ANNOTATION', value = '_')
        submit = st.form_submit_button('TAG')
        if submit:
            try:
                if (tokens[id-1] != form):
                    st.badge('Your ID and FORM does not match! Please correct.', color='red')
                    st.stop()
                elif (deprel != 'root' and head == 0):
                    st.warning('TRY AGAIN! ONLY TOKENS THAT ARE ROOTS SHOULD HAVE HEADS AS ZERO.')
                    st.stop()
                elif (deprel == 'root' and head != 0):
                    st.badge('ANY TOKEN TAGGED AS ROOT SHOULD HAVE THIER HEADS AS ZERO!', color ='red')
                    st.stop()
                else:    
                    df = {'ID':[id],
                        'FORM':[form],
                        'LEMMA':[lemma],
                        'UPOS':[upos],
                        'XPOS':[xpos],
                        'FEATS':[feat],
                        'HEAD':[head],
                        'DEPREL':[deprel],
                        'DEPS':[deps] if deps != f'{head} : {deprel}' else ['_'],
                        'MISC':[misc]
                        }
                    data = pd.DataFrame(df)
                    if 'DATA' not in st.session_state:
                        st.session_state.DATA = data.dropna(how = 'all')
                    else:
                        st.session_state.DATA = data = pd.concat([st.session_state['DATA'], data], ignore_index=True).dropna(how='all')
            except:
                st.warning('THERE IS NOTHING TO TAG!')
                with st.snow():
                    sleep(3)

    if 'DATA' not in st.session_state:
        st.info('TAG A SENTENCE, MAKE EDITS TO AN EXISTING FILE, DOWNLOAD CHANGES OR NEW ANNOTATION IN .conllu or .txt')
    else:
        edit_table = st.toggle('ENABLE TABLE EDIT')        
        if edit_table:
            new_df = st.data_editor(st.session_state.DATA, disabled=False)
            new_df = new_df.dropna(how='any').reset_index()
            del new_df['index']
            new_df['ID'] = new_df['ID'].apply(lambda x:int(x))
            new_df['HEAD'] = new_df['HEAD'].apply(lambda x :int(x))
            st.write('EDITED TABLE:')
            st.table(new_df)
            update = st.button('UPDATE')
            if update:
                st.session_state.DATA = new_df
                st.toast('UPDATE SUCCESSFULL!\nYou can toggle ENABLE TABLE EDIT off now.')
        else:
            st.session_state.DATA = st.session_state.DATA.sort_values(by=['ID']).reset_index()
            del st.session_state.DATA['index']
            st.session_state.DATA['ID'] = st.session_state.DATA['ID'].apply(lambda x:int(x))
            st.session_state.DATA['HEAD'] = st.session_state.DATA['HEAD'].apply(lambda x :int(x))
            st.table(st.session_state.DATA)
        
            cnlu = st.button('CONVERT', help='CONVERT YOUR TAGGED DATA TO CONLL-U FORMAT TO DOWNLOAD')
            if cnlu:
                ID = list(st.session_state.DATA['ID'])
                if len(ID) != len(tokens):
                    st.warning('THERE ARE SOME TOKENS YOU HAVE NOT TAGGED!')
                else:
                    st.balloons()
                    st.toast('DONE!')
                    
                    new = [i[1:] for i in st.session_state.DATA.itertuples()]
                    new = str(new)
                    new = new.\
                    removesuffix(')]').\
                    replace('), (', '\n').\
                    replace('\'\'', '12!@\'').\
                    replace('\'', '').\
                    replace('12!@','\'').\
                    replace(',,', '@#$%  ').\
                    replace(',','  ').\
                    replace('[(', f'\n\n# ANNOTATOR = {st.session_state.USER if 'USER' in st.session_state else 'ANONYMOUS'}\n# Text = {text}\n').\
                    replace('@#$%', ',').\
                    replace('   ', '  ')
                    
                    if 'CONLLU' not in st.session_state:
                        st.session_state.CONLLU = new
                    else:
                        st.session_state.CONLLU+= new

                    with st.expander('SEE YOUR .CONLLU DATA'):
                        st.code(st.session_state.CONLLU)
                    
                    del st.session_state.DATA
                    sent = parse(st.session_state['CONLLU'])
                    with st.popover('Download Options'):
                        st.download_button('As .conllu', st.session_state.CONLLU, file_name='unidep.conllu')
                        st.download_button('As .txt', st.session_state.CONLLU, file_name='unidep.txt')

if __name__ == "__main__":
    st.set_page_config(
    page_title=f"UNIVERSAL DEPENDENCY ANNOTATOR",
    page_icon="🏩",
    layout="wide",
    initial_sidebar_state="auto",
) 
    print(f'\nLOG ISSUES @ {datetime.now().strftime('%H:%M:%S')} (THIS IS NOT AN ISSUE. ONLY CRITICAL ISSUES WILL CRASH THE APP)',
          file = open('log.txt', 'w', buffering=1, errors = 'error'))
    
    function_pages = {
    'INTRO':intro,
    'ANNOTATE': annotate
}
    options = st.sidebar.selectbox('CHOOSE AN ACTION HERE:', function_pages.keys())
    function_pages[options]()
