"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

rcParams['axes.unicode_minus'] = False
rcParams['font.family'] = 'Arial'


date_range = pd.date_range(
    start='2023-01-01', periods=4
)
consume = [1, 2, 3, 4]
# 注意：
price = [[0.45, 0.4, 0.525, 0.675],
         [0.3, 0.325, 0.2, 0.175],
         [0.1, 0.1, 0.125, 0.1],
         [0.15, 0.175, 0.15, 0.05],]
pdf = pd.DataFrame(data=price, columns=date_range, index=consume)
# print(pdf)
index = pdf.index
col = pdf.columns
width = 0.1
plt.bar([i + width * 0 for i in range(len(index))], pdf["2023-01-0" + str(1)], width=width, label="GPT-3.5-Turbo" )
plt.bar([i + width * 1 for i in range(len(index))], pdf["2023-01-0" + str(2)], width=width, label="Code-Llama-34b")
plt.bar([i + width * 2 for i in range(len(index))], pdf["2023-01-0" + str(3)], width=width, label="Claude-instant")
plt.bar([i + width * 3 for i in range(len(index))], pdf["2023-01-0" + str(4)], width=width, label="GPT-4")


# for i in range(7):
#     plt.bar ([j + width * i for j in range (len (index))], pdf["2023-01-0" + str (i+1)], width=width,
#              label="2023-01-0" + str (i+1))
#     print(i)
# plt.xticks([x+width*2 for x in range(4)], index)
legend=plt.legend(loc=0)
custom_labels = ['1-3', '4-6', '7-9', '>=10']
plt.xticks([0.2,1.2,2.2,3.2],custom_labels,)
plt.xlabel('Generation Times')
plt.ylabel('Cases Ratio')

plt.show()
# print(index,col)"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

rcParams['axes.unicode_minus'] = False
rcParams['font.family'] = 'Arial'


date_range = pd.date_range(
    start='2023-01-01', periods=4
)

colors = ['#B3A2C7', '#C3D69B', '#95B3D7', '#D99694']
# colors = ['#8064A2', '#9BBB59', '#4F81BD', '#C0504D']


consume = [1, 2, 3, 4]
# 注意：
price = [[0.5, 0.48, 0.52, 0.68], [0.28, 0.26, 0.16, 0.18], [0.08, 0.10, 0.14, 0.08],
         [0.14, 0.16, 0.18, 0.06], ]


pdf = pd.DataFrame(data=price, columns=date_range, index=consume)
# print(pdf)
index = pdf.index
col = pdf.columns
width = 0.1
fig, ax = plt.subplots(dpi=300)
ax.bar([i + width * 0 for i in range(len(index))], pdf["2023-01-0" +
       str(1)], width=width, label="GPT-3.5-Turbo", color=colors[0])
ax.bar([i + width * 1 for i in range(len(index))], pdf["2023-01-0" +
       str(2)], width=width, label="Code-Llama-34b", color=colors[1])
ax.bar([i + width * 2 for i in range(len(index))], pdf["2023-01-0" +
       str(3)], width=width, label="Claude-instant", color=colors[2])
ax.bar([i + width * 3 for i in range(len(index))],
       pdf["2023-01-0" + str(4)], width=width, label="GPT-4", color=colors[3])


# for i in range(7):
#     plt.bar ([j + width * i for j in range (len (index))], pdf["2023-01-0" + str (i+1)], width=width,
#              label="2023-01-0" + str (i+1))
#     print(i)
# plt.xticks([x+width*2 for x in range(4)], index)
legend = plt.legend(loc=0, fontsize=14)
custom_labels = ['1-3', '4-6', '7-9', '>=10']
plt.xticks([0.2, 1.2, 2.2, 3.2], custom_labels, fontsize=14)
plt.yticks(fontsize=14)
plt.xlabel('Iteration Times', fontsize=16)
plt.ylabel('Samples Ratio', fontsize=16)

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# plt.show()
plt.savefig("figure_aamas.png", dpi=300)
# print(index,col)