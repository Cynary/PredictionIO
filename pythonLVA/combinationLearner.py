import partitionHmmLearner
import simpleLearner

learners = [
    partitionHmmLearner.HMMLearner(2),
    simpleLearner.SimpleLearner()]
alphas = [0.5,0.5]

class CombinationLearner:
    def __init__(self):
        self.name = 'Combination Learner: ' + ','.join([l.name for l in learners])

    def learn(self, data):
        for l in learners:
            l.learn(data)

    def predict(self, user, period):
        prediction = 0
        for a,l in zip(alphas,learners):
            prediction += a*l.predict(user, period)
        return prediction
