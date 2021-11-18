import pandas as pd
import torch
import faiss
import time
import numpy as np
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer

def prepsearch(norm=True, df = None, target = 'content', importing = False):
    ins = SearchEngine(target=target)
    if df is None:
        ins.importCSV("articles.csv")
    else:
        ins.importDf(df)
    if importing:
        ins.importEncoded()
    ins.buildIndex()
    if norm:
        ins.em = np.array(ins.em).astype("float32")
        ins.normalizeEncoded()
    return ins

def summary_prepsearch(csv_path):
    ins = SearchEngine(target="text")
    ins.importCSV(csv_path)
    ins.importEncoded(path=csv_path)
    ins.buildIndex()
    return ins

class SearchEngine():
    def __init__(self,  
            pretrained = "distilbert-base-nli-stsb-mean-tokens",
            target = "content"):
        self.encoder = SentenceTransformer(pretrained)
        self.target = target
        self.em = None
        if torch.cuda.is_available():
            self.encoder = self.encoder.to(torch.device("cuda"))
    
    def importCSV(self, path):
        self.df = pd.read_csv(path)

    def importDf(self, df):
        self.df = df

    def normalizeEncoded(self):
        self.em = normalize(self.em)

    def importEncoded(self, path="embeddings_DistilBert.npy"):
        try:
            self.em = np.load(path)
            self.vecdim = self.em.shape[1]
            print("Encoded text database imported successfully")
        except:
            print("ERROR: CANNOT import encoded text database")

    def buildIndex(self):
        try:
            if self.em is None:
                self.encoder.max_seq_length = 512
                self.em = self.encoder.encode(self.df[self.target].to_list(), show_progress_bar=True)
                self.em = np.array([emi for emi in self.em]).astype("float32")
                self.vecdim = self.em.shape[1]
            #self.index = faiss.IndexFlatL2(self.vecdim)
            self.index = faiss.IndexFlatIP(self.vecdim)
            self.index = faiss.IndexIDMap(self.index)
            self.normalizeEncoded()
            self.index.add_with_ids(self.em, self.df['comment_id'].values)
            print("FAISS index was built successfully")
            print("Number of articles:", self.index.ntotal)
        except:
            print("ERROR: CANNOT build index")
    
    def searchQuery(self, text_query, k=5, to_display = ['text', 'comment_id', 'username']):
        vector_query = self.encoder.encode(list([text_query]))
        vector_query = np.array(vector_query).astype("float32")
        vector_query = normalize(vector_query)
        dists, ids = self.index.search(vector_query, k = k)
        comments = [self.df[self.df['comment_id'] == idx][to_display].to_dict() for idx in ids[0]]
        for idx, dist in enumerate(dists[0]):
            comments[idx]['dist'] = dist
        return comments

    def saveEncoded(self, path = "embs"):
        np.save(path, self.em)

