#!/usr/bin/env python

import numpy as np

class one_dice_trial:
    '''
    The class for one experiment.
    '''
    def __init__(self, M):
        # container for dice rolls
        self.dice_rolls = []
        self.M = M

        # roll the dice
        self.roll_dice_until_sum_exceeds(M)

    def roll_dice(self):
        '''
        Return the result of a dice roll.
        '''
        # np.random.seed(seed=self.random_state)
        return np.random.randint(low=1, high=7)
    
    def roll_dice_until_sum_exceeds(self, M):
        '''
        Roll the dice indefinitely until the sum exceeds M.
        '''
        sum = 0
        self.dice_rolls = []

        # start rolling the dice and record results
        while sum < M:
            res = self.roll_dice()
            sum += res
            self.dice_rolls.append(res)
        # print(f'M={M}\tsum={sum}\nrolls={self.dice_rolls}')
    
    def sum_minus_M(self):
        '''
        Return the sum of dice rolls minus M.
        '''
        return sum(self.dice_rolls) - self.M
    
    def number_of_rolls(self):
        '''
        Return the number of rolls of this trial.
        '''
        return len(self.dice_rolls)
    
class many_dice_trials:
    '''
    The class to accumulate many dice trials and get statistics.
    '''
    def __init__(self, M, ntrials=100):
        self.M = M
        self.ntrials = ntrials
        # containers for answering questions
        self.sum_minus_Ms = []
        self.numbers_of_rolls = []

        # fill the results of the individual experiments
        self.fill_trial_results()

    def fill_trial_results(self):
        '''
        Construct the array of the (sum - M) and number of rolls
        for answering the questions.
        '''
        for i in range(self.ntrials):
            one_trial = one_dice_trial(self.M)
            self.sum_minus_Ms.append(one_trial.sum_minus_M())
            self.numbers_of_rolls.append(one_trial.number_of_rolls())
    
    def mean_of_number_of_rolls(self):
        '''
        Return the mean of the number of rolls.
        '''
        return np.mean(self.numbers_of_rolls)

    def mean_of_sum_minus_M(self):
        '''
        Return the mean of (sum minus M)s.
        '''
        return np.mean(self.sum_minus_Ms)

    def std_of_sum_minus_M(self):
        '''
        Return the standard deviation of (sum minus M)s.
        '''
        return np.std(self.sum_minus_Ms)

if __name__ == '__main__':
    my_dice_trials_m20 = many_dice_trials(20, ntrials=10000)
    my_dice_trials_m5000 = many_dice_trials(5000, ntrials=10000)
    
    # question 1
    print('Answer to question 1: {:.5f}'.format(my_dice_trials_m20.mean_of_sum_minus_M()))

    # question 2
    print('Answer to question 2: {:.5f}'.format(my_dice_trials_m20.mean_of_number_of_rolls()))

    # question 3
    print('Answer to question 3: {:.5f}'.format(my_dice_trials_m20.std_of_sum_minus_M()))

    # question 4
    print('Answer to question 4: {:.5f}'.format(my_dice_trials_m5000.mean_of_sum_minus_M()))

    # question 5
    print('Answer to question 5: {:.5f}'.format(my_dice_trials_m5000.mean_of_number_of_rolls()))

    # question 6
    print('Answer to question 6: {:.5f}'.format(my_dice_trials_m5000.std_of_sum_minus_M()))
