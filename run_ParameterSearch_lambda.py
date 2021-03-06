#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22/11/17

@author: Maurizio Ferrari Dacrema
"""


from Base.non_personalized import TopPop
from KNN.item_knn_CF import ItemKNNCFRecommender
from GraphBased.P3alpha import P3alphaRecommender
from GraphBased.RP3beta import RP3betaRecommender


from data.NetflixEnhanced.NetflixEnhancedReader import NetflixEnhancedReader
from data.Movielens_1m.Movielens1MReader import Movielens1MReader
from data.Movielens_10m.Movielens10MReader import Movielens10MReader
from data.Movielens_20m.Movielens20MReader import Movielens20MReader
from data.BookCrossing.BookCrossingReader import BookCrossingReader
from data.XingChallenge2016.XingChallenge2016Reader import XingChallenge2016Reader
from data.NetflixPrize.NetflixPrizeReader import NetflixPrizeReader


from ParameterTuning.BayesianSearch import BayesianSearch

from data.DataSplitter import DataSplitter_Warm

import numpy as np
import scipy.sparse as sps
import pickle







def runParameterSearch(URM_train, URM_validation, URM_test, dataReader_class, logFilePath ="results/lambda_BPR/", force_positive = True):

    from Lambda.Cython.Lambda_BPR_Cython import Lambda_BPR_Cython

    from ParameterTuning.AbstractClassSearch import DictionaryKeys

    if force_positive:
        positive_name_string = "positive"
    else:
        positive_name_string = "negative"


    ##########################################################################################################

    recommender_class = Lambda_BPR_Cython

    parameterSearch = BayesianSearch(recommender_class, URM_validation, URM_test = URM_test)

    hyperparamethers_range_dictionary = {}
    hyperparamethers_range_dictionary["topK"] = [100, 200, 300, 500]
    hyperparamethers_range_dictionary["pseudoInv"] = [True]
    hyperparamethers_range_dictionary["epochs"] = [5]
    hyperparamethers_range_dictionary["rcond"] = list(np.arange(0.10, 0.3, 0.02))
    hyperparamethers_range_dictionary["lambda_2"] = [1e+1, 1.0, 1e-2, 1e-3, 1e-4, 1e-5, 0.0]
    hyperparamethers_range_dictionary["low_ram"] = [False]
    hyperparamethers_range_dictionary["learning_rate"] = [0.01]
    hyperparamethers_range_dictionary["sgd_mode"] = ["adagrad"]
    hyperparamethers_range_dictionary["batch_size"] = [1]
    hyperparamethers_range_dictionary["force_positive"] = [force_positive]
    hyperparamethers_range_dictionary["initialize"] = ["zero", "random"]#, "one", "random"]

    output_root_path = logFilePath + "Lambda_BPR_Cython_pinv_{}_{}".format(positive_name_string, dataReader_class.DATASET_SUBFOLDER[:-1])


    recommenderDictionary = {DictionaryKeys.CONSTRUCTOR_POSITIONAL_ARGS: [URM_train],
                             DictionaryKeys.CONSTRUCTOR_KEYWORD_ARGS: {"save_eval":False},
                             DictionaryKeys.FIT_POSITIONAL_ARGS: [],
                             DictionaryKeys.FIT_KEYWORD_ARGS: {"URM_validation": URM_validation, "validation_every_n":1,
                                                               "lower_validatons_allowed":2},
                             DictionaryKeys.FIT_RANGE_KEYWORD_ARGS: hyperparamethers_range_dictionary}



    best_parameters = parameterSearch.search(recommenderDictionary, output_root_path = output_root_path, parallelize=False, n_cases=10)


    parameterSearch.evaluate_on_test(URM_test)


    ##########################################################################################################

    recommender_class = Lambda_BPR_Cython

    parameterSearch = BayesianSearch(recommender_class, URM_validation, URM_test = URM_test)

    hyperparamethers_range_dictionary = {}
    hyperparamethers_range_dictionary["topK"] = [100, 200, 300, 500]
    hyperparamethers_range_dictionary["pseudoInv"] = [False]
    hyperparamethers_range_dictionary["epochs"] = [10]
    hyperparamethers_range_dictionary["lambda_2"] = [1e+2, 1e+1, 1.0, 1e-2, 1e-3, 1e-4, 1e-5, 0.0]
    hyperparamethers_range_dictionary["low_ram"] = [False]
    hyperparamethers_range_dictionary["learning_rate"] = [0.01]
    hyperparamethers_range_dictionary["sgd_mode"] = ["adagrad"]
    hyperparamethers_range_dictionary["batch_size"] = [1]
    hyperparamethers_range_dictionary["force_positive"] = [force_positive]
    hyperparamethers_range_dictionary["initialize"] = ["zero", "random"]#, "one", "random"]

    output_root_path = logFilePath + "Lambda_BPR_Cython_transpose_{}_{}".format(positive_name_string, dataReader_class.DATASET_SUBFOLDER[:-1])


    recommenderDictionary = {DictionaryKeys.CONSTRUCTOR_POSITIONAL_ARGS: [URM_train],
                             DictionaryKeys.CONSTRUCTOR_KEYWORD_ARGS: {"save_eval":False},
                             DictionaryKeys.FIT_POSITIONAL_ARGS: [],
                             DictionaryKeys.FIT_KEYWORD_ARGS: {"URM_validation": URM_validation, "validation_every_n":1,
                                                               "lower_validatons_allowed":5},
                             DictionaryKeys.FIT_RANGE_KEYWORD_ARGS: hyperparamethers_range_dictionary}



    best_parameters = parameterSearch.search(recommenderDictionary, output_root_path = output_root_path, parallelize=False, n_cases=10)


    parameterSearch.evaluate_on_test(URM_test)






import os

import traceback
import multiprocessing

from run_ParameterSearch_baseline import read_data_split


def read_data_split_and_search(dataReader_class):


    URM_train, URM_validation, URM_test = read_data_split(dataReader_class)


    runParameterSearch(URM_train, URM_validation, URM_test, dataReader_class, force_positive = True)
    runParameterSearch(URM_train, URM_validation, URM_test, dataReader_class, force_positive = False)



if __name__ == '__main__':

    dataReader_class_list = [
        Movielens1MReader,
        #Movielens10MReader,
        #NetflixEnhancedReader,
        #BookCrossingReader,
        #XingChallenge2016Reader,
        #NetflixPrizeReader
    ]

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
    resultList = pool.map(read_data_split_and_search, dataReader_class_list)
    #
    #
    # for dataReader_class in dataReader_class_list:
    #     try:
    #         read_data_split_and_search(dataReader_class)
    #     except Exception as e:
    #
    #         print("On recommender {} Exception {}".format(dataReader_class, str(e)))
    #         traceback.print_exc()
