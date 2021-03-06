#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 23/10/17

@author: Maurizio Ferrari Dacrema
"""

from Base.Recommender import Recommender
from Base.Recommender_utils import check_matrix
from Base.Similarity_Matrix_Recommender import Similarity_Matrix_Recommender

try:
    from Base.Cython.cosine_similarity import Cosine_Similarity
    #from Base.Cython.cosine_similarity_prune import Cosine_Similarity
except ImportError:
    print("Unable to load Cython Cosine_Similarity, reverting to Python")
    from Base.cosine_similarity import Cosine_Similarity


class ItemKNNCFRecommender(Similarity_Matrix_Recommender, Recommender):
    """ ItemKNN recommender"""

    RECOMMENDER_NAME = "ItemKNNCFRecommender"

    def __init__(self, URM_train, sparse_weights=True):
        super(ItemKNNCFRecommender, self).__init__()

        # CSR is faster during evaluation
        self.URM_train = check_matrix(URM_train, 'csr')

        self.dataset = None

        self.sparse_weights = sparse_weights

    def fit(self, topK=50, shrink=100, similarity='cosine', normalize=True):

        self.topK = topK
        self.shrink = shrink

        self.similarity = Cosine_Similarity(self.URM_train, shrink=shrink, topK=topK, normalize=normalize, mode = similarity)
        #self.similarity = Cosine_Similarity_Parallel(self.URM_train, shrink=shrink, topK=topK, normalize=normalize, mode = similarity)


        if self.sparse_weights:
            self.W_sparse = self.similarity.compute_similarity()
        else:
            self.W = self.similarity.compute_similarity()
            self.W = self.W.toarray()

