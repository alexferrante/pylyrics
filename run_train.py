import numpy as np
import tensorflow as tf
import argparse 
import os
import shutil
import time
import net
import read_data

from constants import *
from tensorflow.python.client import device_lib

def train(source):
  X_train, Y_train, X-dev, Y_dev = read_data.read_batch('mfcc')
  net = net.RNN()
  loss = net.loss()

  train_loss = []
  v_loss = []

  global_step = tf.Variable(0, trainable=False)
  adam_opt = tf.train.AdamOptimizer()

  gradients, var = zip(*adam_opt.compute_gradients(loss))
  gradients, _ = tf.clip_by_global_norm(gradients, clip_norm=1.0)
  optimizer = adam_opt.apply_gradients(zip(gradients, var), global_step=global_step)

  opts = tf.RunOptions(report_tensor_allocations_upon_oom = True)
  with tf.Session() as sess:
    t0 = time.time()
    sess.run(tf.global_variables_initializer(), options=run_options)
    net.load_state(sess, CKPT_PATH)

    n_train_batch = len(X_train)
    i_train = list(range(n_train_batch))

    n_dev_batch = len(X_dev)
    i_dev = list(range(n_dev_batch))

    for e_idx in range(num_epochs):
      np.random.shuffle(i_train)
      epoch_loss = 0

      for i in range(n_train_batch):
        _total_loss, _train_step, n_out = sess.run(
          [_total_loss, optimizer, net()],
          feed_dict={
            net.batchX_placeholder:X_train[i_train[i]],
            net.batchY_placeholder:Y_train[i_train[i]]
          })
        epoch_loss += _total_loss

        if (np.any(np.isnan(n_out))):
          print("\nEpoch: " + repr(epoch_idx) + " Nan")
          
        if source == 1:
          print('Batch Loss:', _total_loss)
      
      print('\nEpoch:' + repr(e_idx) + " || epoch_loss: " + repr(epoch_loss) + " || ", end=' '))
      
      t1 = time.time()
      timer(t0, t1)
      train_loss.append(epoch_loss)

      if e_idx % 10 == 0:
        tf.train.Saver().save(sess, CKPT_PATH, global_step=e_idx)
      
      if e_idx % 1 == 0:
        d_loss_epoch = 0
        for j in range(n_dev_batch):
          _total_dev_loss = sess.run(
            [loss],
            feed_dict={
              net.batchX_placeholder: X_dev[i_dev[j]],
              net.batchY_placeholder: Y_dev[i_dev[j]]
            })
        d_loss_epoch += _total_dev_loss[0]
        print('Epoch: '+ repr(e_idx) + " || Validation Loss: " + repr(d_loss_epoch) + " || ", end=' ')
        v_loss.append(d_loss_epoch)

    tf.train.Saver().save(sess, SAVE_PATH + '/' + repr(time.time()) + '/' + 'save.ckpt')
  
  loss = np.array(loss)
  np.save(SAVE_PATH + 'training_loss.npy', train)
  v_loss = np.array(v_loss)
  np.save(SAVE_PATH + 'validation_loss.npy', v_loss)

def init_path(res):
  if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
  if res == 0:
    if os.path.exists(CKPT_PATH):
      shutil.rmtree(CKPT_PATH)
  if not os.path.exists(CKPT_PATH)
    os.makedirs(CKPT_PATH)

def timer(start, end):
  hours, rem = divmod(end - start, 3600)
  mins, secs = divmod(rem, 60)
  print("timer: {:0>2}:{:0>2}:{:05.2f}".format(
        int(hours), int(mins), secs))

def __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--resume', default=0, help='int, 1 if you want to continue a previous training else 0.', type=int)
  parser.add_argument('--verbose', default=0, help='int, 1 if you want the batch loss else 0.', type=int)
  args = parser.parse_args()
  init_path(args.resume)
  train(args.verbose)