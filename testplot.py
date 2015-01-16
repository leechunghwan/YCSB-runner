from plots import scatter, series

scatter([{'x':[1,2,3], 'y':[8,16,32], 'series':'base2'}, {'x':list(range(6)),
'y':[1,2,4,8,16,32], 'series': 'testb2'}, {'x':list(range(6)),
'y':list(range(6)), 'series':'testlinear'}], 'blah.pdf', xaxis="Testx",
yaxis="Testy")
