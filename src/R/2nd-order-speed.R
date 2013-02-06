setwd("/dvt/workspace/r-ranking-fun/data/raw")
library(ggplot2)
data <- read.csv('citations.2M.data', sep="\t")
data <- read.csv('references.2M.data', sep="\t")

#toplot <- data[,c(2,4)]
#plot(x=toplot$numFound, y=toplot$QTime)

#numFound <- toplot$numFound
#qtime <- toplot$QTime

#ll.d <- lm(numFound ~ qtime)
#plot(ll.d)

p <- ggplot(data, aes(x=numFound, y=QTime)) + geom_point()
p <- p + scale_y_sqrt(breaks=c(10,100, 1000, 10000, 25000))
p <- p + stat_smooth(method="loess", formula = y ~ x, size = 1)
p <- p + labs(title="citations()") + theme(plot.title=element_text(size=30))
print(p)

#savePlot("plots/raw/references-sqrt-scale", type="png", device=dev.cur())



# to print the log scale
p + scale_y_log10(breaks=c(100, 1000, 10000, 20000), labels=c("0.01", "1", "10", "20")) + stat_smooth(method="loess")


cit <- read.csv('citations.no-cache.data', sep="\t")
jcit <- read.csv('joincitations.no-cache.data', sep="\t")
x <- lm(jcit$minQTime ~ jcit$numFound)

cit$nMinQTime <- jcit$minQTime
jcit$nMinQTime <- cit$minQTime

p <- ggplot(jcit, aes(x=numFound, y=minQTime)) + geom_point()
p <- p + scale_y_sqrt(breaks=c(10,100, 1000, 5000, 10000, 20000, 30000))
p <- p + stat_smooth(method="loess", formula = y ~ x, size = 1)
p <- p + labs(title="lucene join") + theme(plot.title=element_text(size=30))
p<- p + geom_line(aes(y = nMinQTime, color="2nd "))
print(p)

p2 <- ggplot(cit, aes(x=numFound, y=minQTime)) + geom_point()
p2 <- p2 + scale_y_sqrt(breaks=c(10,100, 1000, 5000, 10000, 20000, 30000))
p2 <- p2 + stat_smooth(method="loess", formula = y ~ x, size = 1)
p2 <- p2 + labs(title="citations()") + theme(plot.title=element_text(size=30))
p2 <- p2 + geom_line(aes(y = nMinQTime, color="join"))
print(p2)

grid.arrange(p, p2)