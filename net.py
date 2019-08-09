import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os

from constants import *
from tensorflow.contrib.rnn import GRUCell, MultiRNNCell

class RNN:
  def __init__(self):
    self.batchX_placeholder = tf.placeholder(tf.float32, [None, time_max, feature_number])
    self.batchY_placeholder = tf.placeholder(tf.float32, [None, time_max, feature_number])
    self.net = tf.make_template('net', self._net)
    self()
  
  def __call__(self):
    return self.net()
  
  def _net(self):
    cell = MultiRNNCell([GRUCell(hidden_size) for _ in range(n_layer)])
    out_rnn, self.current_state = tf.nn.dynamic_rnn(cell, self.batchX_placeholder, dtype=tf.float32)
    out = tf.layers.dense(inputs=out_rnn, units=feature_number, activation=tf.nn.relu)
    return out
  
  def loss(self):
    out = self()
    return tf.reduce_mean(tf.square(out - self.batchY_placeholder))

  @staticmethod
  def read_state(sess, path):
    ckpt = tf.train.get_checkpoint_state(os.path.dirname(path + '/checkpoint'))
    if ckpt and ckpt.model_checkpoint_path:
      tf.train.Saver().restore(sess, ckpt.model_checkpoint_path)