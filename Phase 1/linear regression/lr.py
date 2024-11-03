#%% md
# importing libraries
#%%
import matplotlib.pyplot as plt
%matplotlib inline
import numpy as np
import pandas as pd
import seaborn as sns
#%% md
# loading train set
#%%
train = pd.read_csv("train.csv")
train.head()
#%% md
# check are all location ids are unique
#%%
duplicates = train[train.duplicated(subset=['id'])]
print(duplicates)
#%% md
# as the first column ('id') is categorical, and also it's unique in each row, it can be dropped because it cannot predict the probability
#%%
train = train.drop(columns=['id'])
#%% md
# now define a function to fill the missing value by knn imputer algorithm
#%%
def euclidean_distance(row1, row2):
    return np.sqrt(np.sum((row1 - row2) ** 2))

def knn_imputer_filling(input_data, k = 5):
    missing_data = [input_data.iloc[i] for i in range(len(input_data)) if input_data.iloc[i].isnull().values.any()]
    complete_data = input_data.dropna()
    for i in range(len(missing_data)):
        distances = []
        for j in range(len(complete_data)):
                dist = euclidean_distance(input_data.iloc[i].values, complete_data.iloc[j].values)
                distances.append((dist, j))
        distances.sort()
        nearest_neighbors = distances[:k]
        for col in input_data.columns:
            if np.isnan(input_data.iloc[i][col]):
                knn_sum = 0
                for dist, idx in nearest_neighbors:
                    knn_sum += complete_data.iloc[idx][col]
                missing_data.at[i, col] = knn_sum / len(nearest_neighbors)
    return complete_data.append(missing_data)
#%% md
# the imputer algorithm takes much time so we define a simple filling function that fill with means
#%%
def simple_filling(input_data):
    for col in input_data.columns:
        mean_value = input_data[col].mean()
        input_data[col].fillna(mean_value, inplace=True)
    return input_data
#%% md
# fill the missing if found
#%% md
# feature extraction part 1: creating correlation heatmap
#%%
correlation_matrix = train.corr()

plt.figure(figsize=(14, 12))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f")
plt.title("Correlation Heatmap")
plt.show()
#%% md
# as we saw, there is no correlation between values so we should extract features by multiplying in 'feature.ipynb' notebook
#%% md
# as the 'DeterioratingInfrastructure' times the other column was made a better correlation, we multiply all column to it and insert a 
#%%
def add_new_features(input_data, effective_column="DeterioratingInfrastructure"):
    new_data = input_data.copy()
    for col in input_data.columns:
        if col != effective_column and col != "FloodProbability":
            new_data[effective_column + '-' + col] = input_data[col] * input_data[effective_column]
    return new_data
#%%
def z_score_scaler(df):
    mean = df.mean()
    std = df.std()
    scaled_df = (df - mean) / std
    return scaled_df, mean, std

def min_max_scaler(df):
    min_val = df.min()
    max_val = df.max()
    scaled_df = (df - min_val) / (max_val - min_val) 
    return scaled_df, min_val, max_val
#%%
def create_datasets(input_data):
    if input_data.isnull().values.any():
        input_data = simple_filling(input_data)
        # train = knn_imputer_filling(train, 10)
    train_feature_plus = add_new_features(input_data)
    tfp_z, tpf_z_mean, tpf_z_std = z_score_scaler(train_feature_plus)
    tfp_m, tpf_m_min, tpf_m_max = min_max_scaler(train_feature_plus)
    train_z, train_z_mean, train_z_std = z_score_scaler(input_data)
    train_m, train_m_min, train_m_max = min_max_scaler(input_data)
    return [tfp_z, tfp_m, train_z, train_m], [[tpf_z_mean, tpf_z_std], [tpf_m_min, tpf_m_max], [train_z_mean, train_z_std], [train_m_min, train_m_max]]
#%%
datasets, scalers = create_datasets(train)
#%%
xs = []
ys = []
for data in datasets:
    y = data['FloodProbability'].to_numpy()
    ys.append(y)
    x = data.drop(['FloodProbability'], axis=1).to_numpy()
    xs.append(x)
xs[0]
#%%
xs[1].shape
#%%
weights = [np.full(xs[i].shape[1], 0.0, dtype=np.float64) for i in range(len(datasets))]
biases = [0.0 for i in range(len(datasets))]
weights
#%%
def linear_regression(epochs_number, initial_learning_rate, intercept, slope, x_train, y_train, momentum=0,
                      patience=np.inf, regularization_param=0, lr_decrease=1, iteration_sample=10000):
    rows, columns = x_train.shape
    mse_serie = []
    mae_serie = []
    learning_rate_serie = []

    # Initialize previous gradients for momentum
    slope_velocity = np.zeros(columns)
    intercept_velocity = 0

    # For early stopping
    best_mse = float('inf')
    patience_counter = 0

    # Initial learning rate
    learning_rate = initial_learning_rate
    total_epoch = epochs_number
    
    # Track per-iteration MSE and MAE for sampling every `iteration_sample` iterations
    mse_per_iteration = []
    mae_per_iteration = []
    sampled_mse = []
    sampled_mae = []
    iteration_counter = 0
    
    for epoch in range(epochs_number):
        total_mse = 0
        total_mae = 0

        for i in range(rows):
            selected_row = x_train[i, :]
            prediction = np.dot(selected_row, slope) + intercept
            real = y_train[i]

            # Calculate gradients with L2 regularization for the slope (not for intercept)
            slope_gradient = selected_row * (prediction - real) * 2 + regularization_param * slope
            intercept_gradient = (prediction - real) * 2

            # Apply momentum
            slope_velocity = momentum * slope_velocity + learning_rate * slope_gradient
            intercept_velocity = momentum * intercept_velocity + learning_rate * intercept_gradient

            # Update parameters
            slope -= slope_velocity
            intercept -= intercept_velocity

            # Calculate errors for MSE and MAE
            iteration_mse = (prediction - real) ** 2
            iteration_mae = abs(prediction - real)
            total_mse += iteration_mse
            total_mae += iteration_mae

            # Store per-iteration errors
            mse_per_iteration.append(iteration_mse)
            mae_per_iteration.append(iteration_mae)

            # Check early stopping and sampling every `iteration_sample` iterations
            if (iteration_counter + 1) % iteration_sample == 0:
                current_sample_mse = np.mean(mse_per_iteration)
                sampled_mse.append(current_sample_mse)
                sampled_mae.append(np.mean(mae_per_iteration))
                mse_per_iteration = []
                mae_per_iteration = []
                
                # Early stopping condition on sample intervals
                if current_sample_mse < best_mse:
                    best_mse = current_sample_mse
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        print(f"Early stopping at iteration {iteration_counter + 1} with MSE: {current_sample_mse}")
                        total_epoch = epoch + 1
                        break
                        
            iteration_counter += 1
        
        # Calculate average errors for the epoch
        mse_val = total_mse / rows
        mae_val = total_mae / rows
        mse_serie.append(mse_val)
        mae_serie.append(mae_val)

        # Learning rate decay
        learning_rate *= lr_decrease
        learning_rate_serie.append(learning_rate)

        # Break loop if early stopping was triggered within the iteration loop
        if patience_counter >= patience:
            break
    
    # Plot MSE and MAE over epochs in separate figures
    
    # Combine all plots into a single figure with subplots.
    fig, axs = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle("Training Metrics Over Epochs and Iterations")

    # Plot MSE per Epoch
    axs[0, 0].plot(range(total_epoch), mse_serie, label='MSE per Epoch', color='blue')
    axs[0, 0].set_xlabel('Epoch')
    axs[0, 0].set_ylabel('MSE')
    axs[0, 0].set_title('MSE per Epoch')
    axs[0, 0].legend()

    # Plot MAE per Epoch
    axs[0, 1].plot(range(total_epoch), mae_serie, label='MAE per Epoch', color='orange')
    axs[0, 1].set_xlabel('Epoch')
    axs[0, 1].set_ylabel('MAE')
    axs[0, 1].set_title('MAE per Epoch')
    axs[0, 1].legend()

    # Plot Sampled MSE per Iteration
    axs[1, 0].plot(range(len(sampled_mse)), sampled_mse, label=f'MSE (Sampled every {iteration_sample} Iterations)', color='purple')
    axs[1, 0].set_xlabel(f'Sample Interval ({iteration_sample} Iterations)')
    axs[1, 0].set_ylabel('Sampled MSE')
    axs[1, 0].set_title(f'Sampled MSE per {iteration_sample} Iterations')
    axs[1, 0].legend()

    # Plot Sampled MAE per Iteration
    axs[1, 1].plot(range(len(sampled_mae)), sampled_mae, label=f'MAE (Sampled every {iteration_sample} Iterations)', color='green')
    axs[1, 1].set_xlabel(f'Sample Interval ({iteration_sample} Iterations)')
    axs[1, 1].set_ylabel('Sampled MAE')
    axs[1, 1].set_title(f'Sampled MAE per {iteration_sample} Iterations')
    axs[1, 1].legend()

    # Plot Learning Rate over Epochs
    axs[2, 0].plot(range(total_epoch), learning_rate_serie, label='Learning Rate per Epoch', color='red')
    axs[2, 0].set_xlabel('Epoch')
    axs[2, 0].set_ylabel('Learning Rate')
    axs[2, 0].set_title('Learning Rate per Epoch')
    axs[2, 0].legend()

    # Remove the empty subplot
    fig.delaxes(axs[2, 1])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    return slope, intercept

#%%
epochs = 5
result_w = weights.copy()
result_b = biases.copy()
for i in range(len(datasets)):
    result_w[i], result_b[i] = linear_regression(epochs, 0.001, biases[i], weights[i], xs[i], ys[i])
#%%

result_w
#%%
def predict(x_test, y_test, slope, intercept):
    y_predicted = np.dot(x_test, slope) + intercept
    mse = np.mean((y_test - y_predicted) ** 2)
    mae = np.mean(np.abs(y_test - y_predicted))
    r2 = 1 - (np.sum((y_test - y_predicted) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
    print(f"Mean Absolute Error: {mae}")
    print(f"Mean Squared Error: {mse}")
    print(f"R2 Score: {r2}")
    return y_predicted
#%%
predicted = []
for i in range(len(datasets)):
    predicted.append(predict(xs[i], ys[i], result_w[i], result_b[i]))

#%%
test = pd.read_csv("test.csv")
test.head()
#%%
test = test.drop(columns=['id'])

#%%
def z_score_scaler_test(input_data, mean, std):
    scaled_df = (input_data - mean) / std
    return scaled_df

def min_max_scaler_test(input_data, min_val, max_val):
    scaled_df = (input_data - min_val) / (max_val - min_val) 
    return scaled_df
#%%

def create_test_datasets(input_data, scaler):
    if input_data.isnull().values.any():
        input_data = simple_filling(input_data)
        # train = knn_imputer_filling(train, 10)
    train_feature_plus = add_new_features(input_data)
    tfp_z = z_score_scaler_test(train_feature_plus, scaler[0][0], scaler[0][1])
    tfp_m = min_max_scaler_test(train_feature_plus, scaler[1][0], scaler[1][1])
    train_z = z_score_scaler_test(input_data, scaler[2][0], scaler[2][1])
    train_m = min_max_scaler_test(input_data,scaler[3][0], scaler[3][1])
    return [tfp_z, tfp_m, train_z, train_m]
#%%
test_datasets = create_test_datasets(test, scalers)
print(test_datasets)
xs_test = []
ys_test = []
for data in test_datasets:
    y = data['FloodProbability'].to_numpy()
    ys_test.append(y)
    x = data.drop(['FloodProbability'], axis=1).to_numpy()
    xs_test.append(x)
#%%
predicted_test = []
for i in range(len(datasets)):
    predicted_test.append(predict(xs_test[i], ys_test[i], result_w[i], result_b[i]))
#%%
weights2 = [np.full(xs[i].shape[1], 0.0, dtype=np.float64) for i in range(len(datasets))]
biases2 = [0.0 for i in range(len(datasets))]

epochs = 20
result_w2 = weights2.copy()
result_b2 = biases2.copy()
for i in range(len(datasets)):
    result_w2[i], result_b2[i]= linear_regression(epochs_number=epochs, initial_learning_rate=0.0001, intercept=biases2[i], slope=weights2[i], x_train=xs[i], y_train=ys[i], momentum=0.5, patience=20, regularization_param=0.0, lr_decrease=.90, iteration_sample=10000)
    

predicted_test2 = []
for i in range(len(datasets)):
    predicted_test2.append(predict(xs_test[i], ys_test[i], result_w2[i], result_b2[i]))
#%%