library("shiny")
library("ggplot2")
library("tidyverse")
library("dplyr")
library("tswge") #so this is what doesn't play nice with rshiny deployment? something to do with bioconductor repo availability??? 
library("cdcfluview")

#shiny app for visualizing ARIMA forecasts for WHO influenza data from India

# import dataset
raw_data  <- read.csv('FluNetInteractiveReport_SE_Asia_1995-2019.csv')
S_Asia <- raw_data[which(raw_data$FLUREGION == 'Southern Asia'), ]
t_ind <- S_Asia[which(S_Asia[1] == 'India'), ] 
t_ind$ALL_INF[is.na(t_ind$ALL_INF)] <- 0

year_range = 1995:2019 #call with year_range[1], ect

# the UI bit:
ui <- fluidPage(
  titlePanel("Adjust Plot Years for WHO Flu Cases: India"),
  sidebarPanel(
    h3('Endpoint ASE Variables'), helpText('Variables for a single forecast using some amount of training and testing data. Evaluated with Average Squared Error'),
    sliderInput(inputId = "num", 
                label = 'Training Data Length (Years)', 
                min = 1, max = 25, value = c(22, 25)),
    sliderInput(inputId = "forecast", 
                label = "Forecast Length (Weeks)", 
                value = 24, min = 1, max = 208)
  ),
  mainPanel(
    plotOutput("p1")
  )
)
# the server bit:
server <- function(input, output) {
  output$p1 <- renderPlot({
    #n_years = input$num #create dataset with 1 years data, 2 years, ect, ect
    range_data = vector()
    for(j in year_range[input$num[1]:input$num[2]]){
      range_data <- rbind(range_data, t_ind[which(t_ind$Year == j), ])
    }
    tdata <- (range_data$ALL_INF) #set primary ts to all influenza cases 
    ttime <- (range_data$SDATE) %>% as.Date("%m/%d/%Y") %>% sort()
    
    pspan = 0:5 #range of values to look for possible p and q coefficients for AR and MA
    qspan = 0:5
    difference = 0
    aic_results <- aic5.wge(tdata, p = pspan, q = qspan) #cut bic results
    aic_results
    m1 = est.arma.wge(tdata, p = aic_results[1, 1], q = aic_results[1, 2], factor = TRUE)
    
    weeks_compare = input$forecast #24 #how many weeks to reserve for testing : 6months 
    f1 <- tdata[1:(length(tdata)-weeks_compare)] %>% fore.aruma.wge(phi = m1$phi, theta = m1$theta, d = difference, n.ahead = weeks_compare)
    mse <- mean((tdata[((length(tdata)-weeks_compare)+1):(length(tdata))] - f1$f)^2)
    paste('Mean Squared Error: ', mse)
    #additional metrics
    #a_metrics <- accuracy(f1$f, tdata[((length(tdata)-weeks_compare)+1):(length(tdata))] )
    
    timeFrame <- data.frame(date = ttime, inf_cases = tdata)
    ggplot(timeFrame)+
      geom_line(aes(x = date, y = tdata, color = 'black'), size = 0.5)+
      geom_line(aes(x = date, y = c(rep(NA, (length(tdata)-weeks_compare)), f1$f), color = 'red'), size= 1) + 
      scale_color_discrete(name = "total_patients", labels = c('actual', 'predicted')) +
      ggtitle(paste('ARIMA (',aic_results[1, 1],',',aic_results[1, 2],',',difference,')', 'Forecast of ', weeks_compare, ' weeks'), subtitle = paste('Mean Squared Error = ', mse))
    
  })
  
  
}

# Run it 
shinyApp(ui = ui, server = server)

