setwd("/dvt/workspace/r-ranking-fun/data/raw")

library(rjson)
library(ggplot2)
require(gridExtra)

json <- fromJSON(file='qf.data.json')

# the simplified version needs to be transformed into a data.frame
d <- data.frame(json$simplified)
l <- unlist(json$simplified)
d <- data.frame(matrix(l[4:length(l)], nrow=length(json$simplified)-1, byrow=T))
names(d) <- l[1:3]

d$hit_position <- as.integer(d$hit_position)
d$factors <- as.factor(d$factors)
d$query <- as.factor(d$query)
d$level <- unclass(d$factors)

# how many records were checked during search
maxhits <- json$params$maxhits

# how wide the each column/building should be 
bwidth <- 5

# we have to modify the data in order to create
# the sky-scraper plot where values are distributed
# across the width of the building
d$hit_window <- sapply(d$hit_position, function(x) x %% bwidth)
d$hit_floor <- sapply(d$hit_position, function(x) {
  round(x / bwidth)
})

#d <- d[1:100,]

# this creates a basic plot where each query is a separate grid
p <- ggplot(d, aes(hit_window, hit_floor)) + geom_tile(mapping=aes(x=hit_window, y=hit_floor, width=0.85, height=0.95))
# the first position becomes the highest
p <- p + scale_y_reverse(breaks=c()) 
# group the values by factor (if i want to ignore quries, i can do: . ~ factors)
p <- p + facet_wrap(query ~ level, ncol=6) 
# remove axes descriptions
p <- p + scale_x_continuous(breaks=c())


# this gets a global plot for all factors
pg <- ggplot(d, aes(hit_window, hit_floor)) + geom_tile(mapping=aes(x=hit_window, y=hit_floor, width=0.85, height=0.95))
pg <- pg + scale_y_reverse(breaks=c()) 
pg <- pg + facet_wrap(. ~ level, ncol=6) 
pg <- pg + scale_x_continuous(breaks=c())

print(p)

leg <- data.frame(factors=unique(d$factors))
legend <- tableGrob(leg)


#grid.arrange(p, legend=legend)
#ll <- by(leg, sapply(leg$factors, function(x) round(unclass(x)/10)), function(a) data.frame(a))

pdf(file="test.pdf", width=7, heigh=50, onefile=T)
layout(matrix(c(1,1,1,2), 4, 1, byrow=TRUE), respect=TRUE)
print(pg)
print(p)
print(grid.arrange(legend))
#print(leg)
dev.off()
