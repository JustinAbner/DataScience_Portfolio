library(ggplot2)
library(readxl)

crime_raw <- read.csv('crimerates-by-state-2005.csv')
crime_df <- crime_raw[-1,]

# Scatter Plot
ggplot(crime_df,aes(population, larceny_theft)) + geom_point(color='blue') +
  ggtitle('R - Scatter Plot')

# Bubble Chart
ggplot(crime_df,aes(population, larceny_theft, size=motor_vehicle_theft)) + 
  geom_point(color='brown', alpha=0.5) + ggtitle('R - Bubble Chart')

# Density Plot
ggplot(crime_df, aes(aggravated_assault)) + geom_density(fill='black') + 
  ggtitle('R - Density Chart')
