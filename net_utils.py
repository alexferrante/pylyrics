import tensorflow as tf
from constants import *

def loss_fn(opt, out, batch):
    # Mean Squared Error
    if opt == 1:
        tmp = tf.subtract(out, batch)
        loss = tf.sqrt(tf.abs(tmp))
    # Kullback Leibler Distance 
    elif opt == 2:
        loss = kl_dist(batch, out)
    return loss

def kl_dist(A, B):
    c1 = tf.multiply(A, tf.log(tf.div(A,B)))
    c2 = tf.subtract(B, A)
    out = tf.summary(c1 + c2)
    return out
