# -*- coding: utf-8 -*-
"""ProjectB1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10WPg2ysb5K6Ku-dw-aTdTGT5gzPvTpcw
"""

import numpy as np
import pandas
import tensorflow as tf
import csv
import pylab as plt

MAX_DOCUMENT_LENGTH = 100
N_FILTERS = 10
FILTER_SHAPE1 = [20, 256]
FILTER_SHAPE2 = [20, 1]
POOLING_WINDOW = 4
POOLING_STRIDE = 2
MAX_LABEL = 15

no_epochs = 100
lr = 0.01
batch_size = 128

tf.logging.set_verbosity(tf.logging.ERROR)
seed = 10
tf.set_random_seed(seed)

def char_cnn_model(x):
  
  input_layer = tf.reshape(tf.one_hot(x, 256), [-1, MAX_DOCUMENT_LENGTH, 256, 1])

  with tf.variable_scope('CNN_0001'):
    conv1 = tf.layers.conv2d(
        input_layer,
        filters=N_FILTERS,
        kernel_size=FILTER_SHAPE1,
        padding='VALID',
        activation=tf.nn.relu)
    pool1 = tf.layers.max_pooling2d(
        conv1,
        pool_size=POOLING_WINDOW,
        strides=POOLING_STRIDE,
        padding='SAME')

  with tf.variable_scope('CNN_0002'):
    conv2 = tf.layers.conv2d(
        pool1,
        filters=N_FILTERS,
        kernel_size=FILTER_SHAPE2,
        padding='VALID',
        activation=tf.nn.relu)
    pool2 = tf.layers.max_pooling2d(
        conv2,
        pool_size=POOLING_WINDOW,
        strides=POOLING_STRIDE,
        padding='SAME')
    pool2 = tf.squeeze(tf.reduce_max(pool2, 1), squeeze_dims=[1])

  logits = tf.layers.dense(pool2, MAX_LABEL, activation=None)

  return input_layer, logits


def read_data_chars():
  
  x_train, y_train, x_test, y_test = [], [], [], []

  with open('train_medium.csv', encoding='utf-8') as filex:
    reader = csv.reader(filex)
    for row in reader:
      x_train.append(row[1])
      y_train.append(int(row[0]))

  with open('test_medium.csv', encoding='utf-8') as filex:
    reader = csv.reader(filex)
    for row in reader:
      x_test.append(row[1])
      y_test.append(int(row[0]))
  
  x_train = pandas.Series(x_train)
  y_train = pandas.Series(y_train)
  x_test = pandas.Series(x_test)
  y_test = pandas.Series(y_test)
  
  
  char_processor = tf.contrib.learn.preprocessing.ByteProcessor(MAX_DOCUMENT_LENGTH)
  x_train = np.array(list(char_processor.fit_transform(x_train)))
  x_test = np.array(list(char_processor.transform(x_test)))
  y_train = y_train.values
  y_test = y_test.values
  
  return x_train, y_train, x_test, y_test

  
def main():
  
  x_train, y_train, x_test, y_test = read_data_chars()

  print(len(x_train))
  print(len(x_test))

  # Create the model
  x = tf.placeholder(tf.int64, [None, MAX_DOCUMENT_LENGTH])
  y_ = tf.placeholder(tf.int64)

  inputs, logits = char_cnn_model(x)

  # Optimizer
  predictions = tf.argmax(logits, axis=1)
  accuracy = tf.contrib.metrics.accuracy(predictions, y_)
  entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=tf.one_hot(y_, MAX_LABEL), logits=logits))
  train_op = tf.train.AdamOptimizer(lr).minimize(entropy)

  sess = tf.Session()
  sess.run(tf.global_variables_initializer())

  # training
  loss = []
  accuracies = []
  for e in range(no_epochs):
    cost = []
    num_minibatches = int(len(x_train) / batch_size)

    idx = np.arange(len(x_train))
    np.random.shuffle(idx)
    X_shuffled, Y_shuffled = x_train[idx], y_train[idx]

    for batch_offset in range(0, len(x_train), batch_size):
        batch_end = min(len(x_train), batch_offset + batch_size)
        minibatch_X, minibatch_Y = X_shuffled[batch_offset:batch_end], Y_shuffled[batch_offset:batch_end]
        _, loss_ = sess.run([train_op, entropy],feed_dict= {x:minibatch_X,y_:minibatch_Y})
        cost.append(loss_)
    loss_ = np.mean(cost)
    loss.append(loss_)

    # measure accuracy
    test_accuracy = sess.run(accuracy, feed_dict={x:x_test,y_:y_test})
    accuracies.append(test_accuracy)

    if e%1 == 0:
      print('iter: %d, entropy: %g, accuracy: %g'%(e, loss[e], accuracies[e]))
  
  sess.close()

  # plot learning curves
  plt.figure(1)
  plt.plot(range(no_epochs), accuracies)
  plt.xlabel(str(no_epochs) + ' iterations')
  plt.ylabel('accuracy')
  plt.title('Accuracy against epochs')
  plt.savefig('./accuracy1.png')

  # plot learning curves
  plt.figure(2)
  plt.plot(range(no_epochs), loss)
  plt.xlabel(str(no_epochs) + ' iterations')
  plt.ylabel('entropy')
  plt.title('Cost entropy against epochs')
  plt.savefig('./epochcost1.png')

if __name__ == '__main__':
  main()