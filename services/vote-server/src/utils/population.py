import numpy as np


def truncated_normal(min_val, max_val, mean, std_dev):
    # Ensure that max_val > min_val
    assert max_val > min_val, "max_val must be greater than min_val"

    # Generate a large number of samples from the normal distribution
    samples = np.random.normal(mean, std_dev, 1000)

    # Truncate the samples to the desired range
    truncated_samples = np.clip(samples, min_val, max_val)

    # Round the truncated samples to the nearest integer
    rounded_samples = np.floor(truncated_samples).astype(int)

    return rounded_samples
