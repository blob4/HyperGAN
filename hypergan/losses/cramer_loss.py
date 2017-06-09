import tensorflow as tf
from hypergan.util.ops import *
from hypergan.util.hc_tf import *
from hypergan.losses.common import *
import hyperchamber as hc

def config(
        reduce=tf.reduce_mean, 
        reverse=False,
        discriminator=None,
        gradient_penalty=False
    ):
    selector = hc.Selector()
    selector.set("reduce", reduce)
    selector.set('reverse', reverse)
    selector.set('discriminator', discriminator)
    selector.set('gradient_penalty',gradient_penalty)

    selector.set('create', create)

    return selector.random_config()

def create(config, gan):
    if(config.discriminator == None):
        d_real = gan.graph.d_real
        d_fake = gan.graph.d_fake
    else:
        d_real = gan.graph.d_reals[config.discriminator]
        d_fake = gan.graph.d_fakes[config.discriminator]

    net = tf.concat([d_real, d_fake], 0)
    net = config.reduce(net, axis=1)
    s = [int(x) for x in net.get_shape()]
    net = tf.reshape(net, [s[0], -1])
    d_real = tf.slice(net, [0,0], [s[0]//2,-1])
    d_fake = tf.slice(net, [s[0]//2,0], [s[0]//2,-1])


    g_loss = d_real - d_fake
    d_loss = -g_loss

    if config.gradient_penalty:
        d_loss += gradient_penalty(gan, config.gradient_penalty)

    gan.graph.d_fake_loss=tf.reduce_mean(d_fake)
    gan.graph.d_real_loss=tf.reduce_mean(d_real)

    return [d_loss, g_loss]