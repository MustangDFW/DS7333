library(shiny)
library(ggplot2)
library(tidyverse)
library(cdcfluview)
library(tseries)
library(forecast)

raw_data  <- read.csv('FluNetInteractiveReport_SE_Asia_1995-2019.csv')
S_Asia <- raw_data[which(raw_data$FLUREGION == 'Southern Asia'), ]
t_ind <- S_Asia[which(S_Asia[1] == 'India'), ] 
t_ind$ALL_INF[is.na(t_ind$ALL_INF)] <- 0
year_range = 1995:2019 #call with year_range[1], ect

# the UI bit:
ui <- fluidPage(
  titlePanel("Adjust Plot Years for WHO Flu Cases: India"),
  sidebarPanel(
    h3('Endpoint ASE Variables'), helpText('Variables for a single forecast using some amount of training and testing data. Evaluated with Average Squared Error as primary metric. \n Image refresh may take a few seconds'),
    sliderInput(inputId = "num", 
                label = 'Training Data Length (Years)', 
                min = 1, max = 25, value = c(22, 25)),
    sliderInput(inputId = "forecast", 
                label = "Forecast Length (Weeks)", 
                value = 24, min = 1, max = 208)
  ),
  mainPanel(
    plotOutput("p1")#,
    #verbatimTextOutput("t1") #necessary for multi lineoutput
  )
)

server <- function(input, output) {
  output$p1 <- renderPlot({
    
    #n_years = input$num #create dataset with 1 years data, 2 years, based on slider input
    range_data = vector()
    for(j in year_range[input$num[1]:input$num[2]]){
      range_data <- rbind(range_data, t_ind[which(t_ind$Year == j), ])
    }
    tdata <- (range_data$ALL_INF) #set primary ts to all influenza cases 
    ttime <- (range_data$SDATE) %>% as.Date("%m/%d/%Y") %>% sort()
    
    test_interval = input$forecast #weeks
    ttrain <- tdata[1:(length(tdata)-test_interval)]
    ttest <- tdata[(length(tdata)-test_interval+1):length(tdata)]
    #aic5.wge approximation
    holder_matrix <- matrix(0, nrow = 6*2*6, ncol = 4)
    j = 1
    for(p in 0:5) for(d in 0:1) for(q in 0:5){
      holder_matrix[j, ] <- c(p, d, q, AIC(arima(tdata, order = c(p, d ,q))) )
      j <- j+1
    }
    df_a <- as.data.frame(holder_matrix)
    names(df_a) <- c('p', 'd', 'q', 'aic')
    aic_df <- df_a[order(df_a$aic, decreasing = FALSE), ] #order so that lowest aic is at the top
    #head(aic_df) #shows top 5 aic values for pdq permutations
    
    #fit model using aic values
    f<- arima(ttrain, order = c(aic_df[1, 1], aic_df[1, 2] , 0)) %>% forecast(test_interval)
    ase <- mean((f$mean - ttest)^2)
    extra_metrics <- accuracy(f$mean, ttest)
    
    timeframe = data.frame(date = ttime, actual = tdata, train = c(ttrain, rep(NA, test_interval)), pred = c(rep(NA, (length(ttrain))), f$mean))
    
    ggplot(timeframe) + 
      geom_line(aes(x = date, y = actual, col = 'actual'))+
      geom_line(aes(x = date, y = train, col = 'training data')) +
      geom_line(aes(x = date, y = pred, col = 'predictions')) +
      ggtitle(paste('Total Influenza Case Predictions: ARIMA(', aic_df[1, 1], ',',aic_df[1, 2], ',','0', ')'), subtitle = paste('ASE for', test_interval, 'week prediction: ', ase)) +
      xlab('Date') + ylab('Total Cases')
  })
  #output$t1 <- renderText({
  #  paste('Additional Metrics:', 
  #        paste('\nME: ', extra_metrics[1]),
  #        paste('\nRMSE: ', extra_metrics[2]),
  #        paste('\nMAE: ', extra_metrics[3]),
  #        paste('\nMPE: ', extra_metrics[4]),
  #        paste('\nMAPE: ', extra_metrics[5]), sep = '\n')
  #})
}

# Run it 
shinyApp(ui = ui, server = server)

