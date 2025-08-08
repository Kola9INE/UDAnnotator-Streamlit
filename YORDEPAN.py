import streamlit as st
import pandas as pd
from functools import reduce
from datetime import datetime
import string
from time import sleep
from conllu import parse
from streamlit.errors import StreamlitValueAboveMaxError as SVAME

def tokenize(text:str):
    letters = [char for char in text]
    new = []
    for char in letters:
        if char not in list(string.punctuation):
            new.append(char)
        else:
            new.extend([' ',char,' '])
    tokens = reduce(lambda x,y:x+y, new)
    for i in tokens.split(' ')[:-1]:
        yield(i)

def intro():
    st.header("WELCOME!\n")
    st.subheader('THIS IS A WEBAPP TO ANNOTATE THE TOKENS PER SENTENCE FOR A DEPENDENCY PARSE TREE. THE RESULT CAN BE EXPORTED AS .TXT OR .CONLLU FORMAT')
    st.write('Kindly proceed to the **ANNOTATE** page to start annotating your sentences.')

#     st.markdown('''\n
#                 The dependency parsing is one of the many approaches to answering the question: `HOW CAN A MACHINE UNDERSTAND THE SYNTAX OF A LANGUAGE?`
#                 This approach is based on the assumption that **every sentence has _at least, one root_ while other neighbouring tokens share a relationship with the head and/or with other tokens.**
#                 It is this relationship (at individual token level) we are majorly particular about in dependency syntax. In order to train models or build one using a dependency treebank,
#                 tokens of sentences are tagged in the format that have been universally agreed in the CoNLL. This format is named the CoNNL-U format, this format highlights ten features per tokens in a document/sentence.
#                 The ten features include the:
#                 * **ID**: This is the index of an individual token in a document/sentence. The index of a token is usually {x | x + 1 ϵ N}. Or simply put, the index of a number is usually from 1 to positive infinity and must be an integer.
#                 * **FORM**: This is usually the surface level representation of the token selected for annotation - as it is in the sentence. 
#                 * **LEMMA**: This is the root form of the token selected. The lemma of a token is usually the dictionary form of the token selected. For example, the lemma of the token `running` is `run`.
# ''')

def annotate():
    UPOS = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X']
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
                    'dep':'determiner',
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

    tokens = []
    text = st.text_area('INPUT TEXT HERE:', placeholder='PLEASE ONLY INPUT ONE SENTENCE HERE. IT MAY BE SIMPLE, COMPOUND, COMPLEX OR COMPOUND-COMPLEX.')
    button = st.button('ANNOTATE')
    if button:
        if not text:
            st.subheader('There is nothing to annotate!'.upper())  

    try:
        tokens = [token for token in list(tokenize(text)) if token]
    except TypeError:
        pass
    form = st.selectbox('SELECT WORD TO TAG HERE', options = tokens)

    with st.form(key='form', clear_on_submit=False, enter_to_submit=False, border=False):
        col1, col2, col3 = st.columns(3)
        col2.metric('TOKEN SELECTED:', value=form, border = True, width = 'content')
        try:
            id = st.number_input('SELECT ID HERE', min_value=1, max_value=len(tokens))
        except SVAME:
            id = st.number_input('SELECT ID HERE:', min_value=0, max_value=0)
        col1, col2, col3 = st.columns(3)
        lemma = col1.text_input('ENTER LEMMA HERE', value = form.lower() if form else None)
        upos = col2.selectbox('SELECT UNIVERSAL PART OF SPEECH HERE:', options = UPOS, index = 1)
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
                    st.badge('ANY TOKEN THAT ARE TAGGED AS ROOT SHOULD HAVE THIER HEADS AS ZERO!', color ='red')
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
        st.info('TAG A SENTENCE, MAKE EDIT, DOWNLOAD IN .conllu or .txt')
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
                    replace('\'', '').\
                    replace(',,', '@#$%  ').\
                    replace(',','  ').\
                    replace('[(', f'\n\n# Text = {text}\n').\
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