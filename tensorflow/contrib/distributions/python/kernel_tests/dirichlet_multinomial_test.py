# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf


class DirichletMultinomialTest(tf.test.TestCase):

  def testSimpleShapes(self):
    with self.test_session():
      alpha = np.random.rand(3)
      dist = tf.contrib.distributions.DirichletMultinomial(1., alpha)
      self.assertEqual(3, dist.event_shape().eval())
      self.assertAllEqual([], dist.batch_shape().eval())
      self.assertEqual(tf.TensorShape([3]), dist.get_event_shape())
      self.assertEqual(tf.TensorShape([]), dist.get_batch_shape())

  def testComplexShapes(self):
    with self.test_session():
      alpha = np.random.rand(3, 2, 2)
      n = [[3., 2], [4, 5], [6, 7]]
      dist = tf.contrib.distributions.DirichletMultinomial(n, alpha)
      self.assertEqual(2, dist.event_shape().eval())
      self.assertAllEqual([3, 2], dist.batch_shape().eval())
      self.assertEqual(tf.TensorShape([2]), dist.get_event_shape())
      self.assertEqual(tf.TensorShape([3, 2]), dist.get_batch_shape())

  def testNproperty(self):
    alpha = [[1., 2, 3]]
    n = [[5.]]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(n, alpha)
      self.assertEqual([1, 1], dist.n.get_shape())
      self.assertAllClose(n, dist.n.eval())

  def testAlphaProperty(self):
    alpha = [[1., 2, 3]]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(1, alpha)
      self.assertEqual([1, 3], dist.alpha.get_shape())
      self.assertAllClose(alpha, dist.alpha.eval())

  def testPmfNandCountsAgree(self):
    alpha = [[1., 2, 3]]
    n = [[5.]]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(n, alpha)
      dist.pmf([2, 3, 0]).eval()
      dist.pmf([3, 0, 2]).eval()
      with self.assertRaisesOpError('Condition x >= 0.*'):
        dist.pmf([-1, 4, 2]).eval()
      with self.assertRaisesOpError('Condition x == y.*'):
        dist.pmf([3, 3, 0]).eval()

  def testPmfArbitraryCounts(self):
    alpha = [[1., 2, 3]]
    n = [[5.]]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(n, alpha)
      dist.pmf([2., 3, 0]).eval()
      dist.pmf([3., 0, 2]).eval()
      dist.pmf([3.0, 0, 2.0]).eval()
      # Both equality and integer checking fail.
      with self.assertRaisesOpError('Condition x == y.*'):
        dist.pmf([1.0, 2.5, 1.5]).eval()
      dist = tf.contrib.distributions.DirichletMultinomial(
          n, alpha, allow_arbitrary_counts=True)
      dist.pmf(np.array([1.0, 2.5, 1.5])).eval()

  def testPmfBothZeroBatches(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      # Both zero-batches.  No broadcast
      alpha = [1., 2]
      counts = [1., 0]
      dist = tf.contrib.distributions.DirichletMultinomial(1, alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(1 / 3., pmf.eval())
      self.assertEqual((), pmf.get_shape())

  def testPmfBothZeroBatchesNontrivialN(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      # Both zero-batches.  No broadcast
      alpha = [1., 2]
      counts = [3., 2]
      dist = tf.contrib.distributions.DirichletMultinomial(5, alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(1 / 7., pmf.eval())
      self.assertEqual((), pmf.get_shape())

  def testPmfBothZeroBatchesMultidimensionalN(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      alpha = [1., 2]
      counts = [3., 2]
      n = np.full([4, 3], 5.)
      dist = tf.contrib.distributions.DirichletMultinomial(n, alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose([[1 / 7., 1 / 7., 1 / 7.]] * 4, pmf.eval())
      self.assertEqual((4, 3), pmf.get_shape())

  def testPmfAlphaStretchedInBroadcastWhenSameRank(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      alpha = [[1., 2]]
      counts = [[1., 0], [0., 1]]
      dist = tf.contrib.distributions.DirichletMultinomial([1], alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose([1 / 3., 2 / 3.], pmf.eval())
      self.assertEqual((2), pmf.get_shape())

  def testPmfAlphaStretchedInBroadcastWhenLowerRank(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      alpha = [1., 2]
      counts = [[1., 0], [0., 1]]
      pmf = tf.contrib.distributions.DirichletMultinomial(1., alpha).pmf(counts)
      self.assertAllClose([1 / 3., 2 / 3.], pmf.eval())
      self.assertEqual((2), pmf.get_shape())

  def testPmfCountsStretchedInBroadcastWhenSameRank(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      alpha = [[1., 2], [2., 3]]
      counts = [[1., 0]]
      pmf = tf.contrib.distributions.DirichletMultinomial(
          [1., 1.], alpha).pmf(counts)
      self.assertAllClose([1 / 3., 2 / 5.], pmf.eval())
      self.assertEqual((2), pmf.get_shape())

  def testPmfCountsStretchedInBroadcastWhenLowerRank(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    with self.test_session():
      alpha = [[1., 2], [2., 3]]
      counts = [1., 0]
      pmf = tf.contrib.distributions.DirichletMultinomial(1., alpha).pmf(counts)
      self.assertAllClose([1 / 3., 2 / 5.], pmf.eval())
      self.assertEqual((2), pmf.get_shape())

  def testPmfForOneVoteIsTheMeanWithOneRecordInput(self):
    # The probabilities of one vote falling into class k is the mean for class
    # k.
    alpha = [1., 2, 3]
    with self.test_session():
      for class_num in range(3):
        counts = np.zeros((3), dtype=np.float32)
        counts[class_num] = 1
        dist = tf.contrib.distributions.DirichletMultinomial(1., alpha)
        mean = dist.mean().eval()
        pmf = dist.pmf(counts).eval()

        self.assertAllClose(mean[class_num], pmf)
        self.assertTupleEqual((3,), mean.shape)
        self.assertTupleEqual((), pmf.shape)

  def testMeanDoubleTwoVotes(self):
    # The probabilities of two votes falling into class k for
    # DirichletMultinomial(2, alpha) is twice as much as the probability of one
    # vote falling into class k for DirichletMultinomial(1, alpha)
    alpha = [1., 2, 3]
    with self.test_session():
      for class_num in range(3):
        counts_one = np.zeros((3), dtype=np.float32)
        counts_one[class_num] = 1.
        counts_two = np.zeros((3), dtype=np.float32)
        counts_two[class_num] = 2

        dist1 = tf.contrib.distributions.DirichletMultinomial(1., alpha)
        dist2 = tf.contrib.distributions.DirichletMultinomial(2., alpha)

        mean1 = dist1.mean().eval()
        mean2 = dist2.mean().eval()

        self.assertAllClose(mean2[class_num], 2 * mean1[class_num])
        self.assertTupleEqual((3,), mean1.shape)

  def testZeroCountsResultsInPmfEqualToOne(self):
    # There is only one way for zero items to be selected, and this happens with
    # probability 1.
    alpha = [5, 0.5]
    counts = [0., 0]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(0., alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(1.0, pmf.eval())
      self.assertEqual((), pmf.get_shape())

  def testLargeTauGivesPreciseProbabilities(self):
    # If tau is large, we are doing coin flips with probability mu.
    mu = np.array([0.1, 0.1, 0.8], dtype=np.float32)
    tau = np.array([100.], dtype=np.float32)
    alpha = tau * mu

    # One (three sided) coin flip.  Prob[coin 3] = 0.8.
    # Note that since it was one flip, value of tau didn't matter.
    counts = [0, 0, 1]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(1., alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(0.8, pmf.eval(), atol=1e-4)
      self.assertEqual((), pmf.get_shape())

    # Two (three sided) coin flips.  Prob[coin 3] = 0.8.
    counts = [0, 0, 2]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(2, alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(0.8**2, pmf.eval(), atol=1e-2)
      self.assertEqual((), pmf.get_shape())

    # Three (three sided) coin flips.
    counts = [1., 0, 2]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(3, alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(3 * 0.1 * 0.8 * 0.8, pmf.eval(), atol=1e-2)
      self.assertEqual((), pmf.get_shape())

  def testSmallTauPrefersCorrelatedResults(self):
    # If tau is small, then correlation between draws is large, so draws that
    # are both of the same class are more likely.
    mu = np.array([0.5, 0.5], dtype=np.float32)
    tau = np.array([0.1], dtype=np.float32)
    alpha = tau * mu

    # If there is only one draw, it is still a coin flip, even with small tau.
    counts = [1., 0]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(1., alpha)
      pmf = dist.pmf(counts)
      self.assertAllClose(0.5, pmf.eval())
      self.assertEqual((), pmf.get_shape())

    # If there are two draws, it is much more likely that they are the same.
    counts_same = [2, 0]
    counts_different = [1, 1.]
    with self.test_session():
      dist = tf.contrib.distributions.DirichletMultinomial(2, alpha)
      pmf_same = dist.pmf(counts_same)
      pmf_different = dist.pmf(counts_different)
      self.assertLess(5 * pmf_different.eval(), pmf_same.eval())
      self.assertEqual((), pmf_same.get_shape())


if __name__ == '__main__':
  tf.test.main()
