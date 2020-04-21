'''This script implements the paper of Multi-View Unsupervised User Feature Embedding for Social Media-based Substance Use Prediction: Post-D-DBOW
'''

import gensim
from gensim.models.doc2vec import Doc2Vec
import sys
import os
import numpy as np


class Doc2User(object):
    '''Apply Doc2Vec model on the documents to generate user and product representation.
        Outputs will be one user/product_id + vect per line.

        Parameters
        ----------
        task: str
            Task name, such as amazon, yelp and imdb
        model_path: str
            Path of LDA model file
    '''
    def __init__(self, task, model_path):
        self.task = task
        self.model = self.__load_model(model_path)
        self.model.delete_temporary_training_data(
            keep_doctags_vectors=True, keep_inference=True)

    def __load_model(self, model_path):
        return Doc2Vec.load(model_path)

    def doc2item(self, data_path, opath, id_idx=2, mode='average'):
        '''Extract user vectors from the given data path

            Parameters
            ----------
            data_path: str
                Path of data file, tsv file
            opath: str
                Path of output path for user vectors
            id_idx: int
                Index of id, 2 is for user, 1 is for product
        '''
        item_dict = dict()
        ofile = open(opath, 'w')

        print('Loading Data')
        with open(data_path) as dfile:
            dfile.readline() # skip the column names

            for line in dfile:
                line = line.strip().split('\t')

                tid = line[id_idx]
                text = line[3]
                if tid not in item_dict:
                    item_dict[tid] = []

                # collect data
                if mode == 'average':
                    item_dict[tid].append(text.split())
                else:
                    if len(item_dict[tid]) == 0:
                        item_dict[tid].append(text.split())
                    else:
                        item_dict[tid][0].extend(text.split())

        for tid in list(item_dict.keys()):
            print(tid)
            # encode the document by doc2vec
            item_dict[tid] = np.asarray([
                self.model.infer_vector(doc) for doc in item_dict[tid]
            ])
            # average the lda inferred documents
            item_dict[tid] = np.mean(item_dict[tid], axis=0)

            # write to file
            ofile.write(tid + '\t' + ' '.join(map(str, item_dict[tid])))

            # save memory
            del item_dict[tid]
        ofile.flush()
        ofile.close()


if __name__ == '__main__':
    task = sys.argv[1]
    raw_dir = '../data/raw/'
    task_data_path = raw_dir + task + '/' + task + '.tsv'

    data_dir = raw_dir + task + '/'
    baseline_dir = '../resources/baselines/'
    task_dir = baseline_dir + task + '/'
    odir = task_dir + 'doc2user/'
    opath_user = odir + 'user.txt'
    opath_product = odir + 'product.txt'

    resource_dir = '../resources/embedding/'
    model_path = resource_dir + task + '/doc2v.model'

    # create directories
    if not os.path.exists(baseline_dir):
        os.mkdir(baseline_dir)
    if not os.path.exists(task_dir):
        os.mkdir(task_dir)
    if not os.path.exists(odir):
        os.mkdir(odir)

    # Doc2User
    d2u = Doc2User(task, model_path)
    # user vectors
    d2u.doc2item(
        data_path=task_data_path, 
        opath=opath_user, 
        id_idx=2
    )
    # product vectors
    d2u.doc2item(
        data_path=task_data_path, 
        opath=opath_product, 
        id_idx=1
    )
