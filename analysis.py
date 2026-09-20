import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data\\moscow_flats_dataset_eng.csv")

pd.set_option('display.float_format', '{:.2f}'.format)

def print_info(df):
    print('head:\n', df.head())
    print('\nshape:\n', df.shape) 
    print('\ncolumns:\n', df.columns)
    print('\ntypes:\n', df.dtypes)
    print('\ninfo:')
    df.info()
    print('\npercentage of missing values ​​for each column:\n', df.isna().mean() * 100)


def suspicious_values(df):
    invalid_space = df['total_area'] <= 0
    invalid_price = df['price'] <= 0
    invalid_rooms = df['number_of_rooms'] < 0
    invalid_floor = df['floor'] > df['number_of_floors']

    max_space_limit = 500  
    unrealistic_space = df['total_area'] > max_space_limit
    
    all_anomalies = invalid_space | invalid_price | invalid_rooms | invalid_floor | unrealistic_space
    
    suspicious_df = df[all_anomalies]
    print(f"Suspicious lines found: {len(suspicious_df)}")
    return suspicious_df


def delete_erroneous_values(df):
    df = df.drop_duplicates()

    df['ceiling_height'] = df['ceiling_height'].fillna(df['ceiling_height'].median())
    df = df.dropna(subset=['number_of_floors'])

    df = df[(df['total_area'] > 0) &
            (df['price'] > 0) &
            (df['number_of_rooms'] >= 0) &
            (df['floor'] > 0) &
            (df['floor'] <= df['number_of_floors']) &
            (df['number_of_floors'] > 0) &
            (df['ceiling_height'] > 0)
            ]
    return df

df = delete_erroneous_values(df)

def price_visualization(df):

    _, ax = plt.subplots(figsize=(10, 6))

    bins = np.logspace(np.log10(df['price'].min()), np.log10(df['price'].max()), 50)

    ax.hist(df['price'], bins=bins, color='skyblue', edgecolor='white', alpha=0.8)
    
    ax.set_xscale('log')

    median_val = df['price'].median()
    mean_val = df['price'].mean()

    ax.axvline(median_val, color='red', linestyle='--', label=f'Median: {median_val:.0f}')
    ax.axvline(mean_val, color='orange', linestyle='-', label=f'Mean: {mean_val:.0f}')

    ticks = [1e6, 5e6, 1e7, 3e7, 1e8, 5e8, 1e9, 4e9]
    tick_labels = ['1 mln', '5 mln', '10 mln', '30 mln', '100 mln', '500 mln', '1 bln', '4 bln']
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    
    ax.set_title('Distribution of real estate prices')
    ax.set_xlabel('Price (logarithmic scale)')
    ax.set_ylabel('Number of objects')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.legend(fontsize=11)

    plt.savefig('results/price_distribution.png')
    plt.close()


def area_visualization(df):
    _, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df['total_area'], bins=50, color='skyblue', edgecolor='white', alpha=0.8)

    median_val = df['total_area'].median()
    mean_val = df['total_area'].mean()

    ax.axvline(median_val, color='red', linestyle='--', label=f'Median: {median_val:.0f}')
    ax.axvline(mean_val, color='orange', linestyle='-', label=f'Mean: {mean_val:.0f}')
    

    ax.set_title('Distribution of real estate area')
    ax.set_xlabel('Area, m$^2$')
    ax.set_ylabel('Number of objects')
    ax.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.savefig('results/area_distribution.png')
    plt.close()



def area_and_price_visualization(df):
    _, ax = plt.subplots(figsize=(10, 6))
    
    df['price_mln'] = df['price'] / 1_000_000
    ax.scatter(df['total_area'], df['price_mln'], alpha=0.3, s=10, color='blue')
    
    ax.set_yscale('log')

    ticks = [1, 10, 100, 1000]
    tick_labels = ['1 mln', '10 mln', '100 mln', '1 bln']
    ax.set_yticks(ticks)
    ax.set_yticklabels(tick_labels)

    ax.set_title('Relationship between area and price')
    ax.set_xlabel('Area, m$^2$')
    ax.set_ylabel('Price, RUB')

    plt.savefig('results/area_price_scatter.png')
    plt.close()



def print_corr(df):
    print('correlation between price and area:\n',df[['total_area', 'price']].corr())


df['price_per_m2'] = df['price'] / df['total_area']


def price_per_square_meter_analysis(df):

    mean_val = df['price_per_m2'].mean()
    median_val = df['price_per_m2'].median()

    Q1 = df['price_per_m2'].quantile(0.25)
    Q3 = df['price_per_m2'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df['price_per_m2'] < lower_bound) | (df['price_per_m2'] > upper_bound)]

    #distribution
    _,ax = plt.subplots(figsize=(10,6))
    ax.hist(df['price_per_m2'], bins=50, color='skyblue', edgecolor='white', alpha=0.8)
    
    ax.set_xscale('log')

    ticks = [1e5, 2e5, 5e5, 1e6, 2e6, 5e6]
    tick_labels = ['100k', '200k', '500k', '1 mln', '2 mln', '5 mln']

    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)

    ax.axvline(median_val, color='red', linestyle='--', label=f'Median: {median_val:.0f}')
    ax.axvline(mean_val, color='orange', linestyle='-', label=f'Mean: {mean_val:.0f}')
    
    ax.set_title('Distribution of price per square meter for real estate properties')
    ax.set_xlabel('Price per m$^2$, RUB (log scale)')
    ax.set_ylabel('Number of objects')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    
    plt.savefig('results/price_per_square_meter_distribution.png')
    plt.close()

    return{
        'average price per m^2': mean_val,
        'median price per m^2' : median_val,
        'outliers' : outliers,
        'outliers_count': len(outliers),
        'outliers_bounds': (lower_bound, upper_bound),
        'distribution' : 'saved in the "results" folder'
        }

def analysis_of_regions(df):
    
    result = df.groupby('region_of_moscow').agg({
        'price' : 'median',
        'price_per_m2' : 'median',
        'region_of_moscow' : 'count'
        })
    result = result.rename(columns={
        'price': 'median_price',
        'price_per_m2': 'median_price_per_m2',
        'region_of_moscow': 'count'
    })
    return result


def region_price_per_m2_visualization(df):
    _, ax = plt.subplots(figsize=(10, 6))

    median_prices = df.groupby('region_of_moscow')['price_per_m2'].median()
    ax.bar(median_prices.index, median_prices.values, color='lightblue')
    
    ax.set_title('Median price per m$^2$ by region')
    ax.set_xlabel('Region')
    ax.set_ylabel('Median price per m$^2$, RUB')
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    plt.savefig('results/region_price_per_m2.png')
    plt.close()


def main():
    price_visualization(df)
    area_visualization(df)
    area_and_price_visualization(df)
    price_per_square_meter_analysis(df)
    analysis_of_regions(df)
    region_price_per_m2_visualization(df)



if __name__ == "__main__":
    main()