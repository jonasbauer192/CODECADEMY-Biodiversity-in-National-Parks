from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np

path = "D:\CODECADEMY-Biodiversity-in-National-Parks"
fileName1 = "observations.csv"
fileName2 = "species_info.csv"

class dataFrameClass:

    def __init__(self, path, fileName1, fileName2):
        self.path = path
        self.fileName1 = fileName1
        self.fileName2 = fileName2
        self.createDataframe()
        self.cleanDataframe()
        self.countDataframe()
        self.overviewDataframe()

    def createDataframe(self):
        os.chdir(path)
        df1 = pd.read_csv(self.fileName1)
        df2 = pd.read_csv(self.fileName2)
        self.dataframe = pd.merge(df1, df2)

    def cleanDataframe(self):
        self.dataframe = self.dataframe.drop_duplicates(subset=["common_names"])
        self.dataframe = self.dataframe.dropna()
        self.dataframe = self.dataframe.drop(columns=["scientific_name", "common_names"])
        self.dataframe.columns = ["Park", "Observations", "Category", "Status"]

    def countDataframe(self):
        df1 = self.dataframe.groupby("Category")["Observations"].sum().reset_index()

        self.dataframe["Count"] = 1
        df2 = self.dataframe.groupby(["Category", "Status"])["Count"].sum().reset_index()
        lst = []
        for category in df2["Category"].unique():
            filteredDf = df2[df2["Category"] == category]
            # if the df does not contain a row for a status entry create it and set its count to 0
            for status in df2["Status"].unique():
                if not status in filteredDf["Status"].unique():
                    df2 = df2.append(
                        {"Category": category, "Status": status, "Count": 0}, ignore_index=True)

        self.countDataframe = pd.merge(df1, df2)

    def overviewDataframe(self):

        proportion = lambda row: (row["Count"]/row["Observations"]) * 100
        self.countDataframe["Proportion"] = self.countDataframe.apply(proportion, axis=1)
        self.countDataframe.drop(columns=["Observations"])
        df1 = self.countDataframe.pivot(
            index="Category",
            columns="Status",
            values="Count").reset_index()
        df2 = self.countDataframe.pivot(
            index="Category",
            columns="Status",
            values="Proportion").reset_index()

class PlotClass:
    def __init__(self, dfObj):
        self.dfObj = dfObj
        self.statusOrder = {"In Recovery": "tab:green", "Species of Concern": "tab:olive",
                            "Threatened": "tab:orange", "Endangered": "tab:red"}
        self.categoryOrder = {"Amphibian": "tab:blue", "Bird": "tab:orange",
                              "Fish": "tab:green", "Mammal": "tab:red",
                              "Nonvascular Plant": "tab:purple", "Reptile": "tab:brown",
                              "Vascular Plant": "tab:pink"}
        self.stackedBarcharts()
        self.pieCharts()
        self.correlationPlot()

    def stackedBarcharts(self):

        scopes = ["Count", "Proportion"]
        xval = ["Status", "Category"]
        order = [self.categoryOrder.keys(), self.statusOrder.keys()]
        column2drop = ["Category", "Status"]
        palette = [self.categoryOrder, self.statusOrder]

        subplotCounter = 1
        for scope in scopes:
            # loop to create a single subplot
            for i in range(len(xval)):
                df = self.dfObj.countDataframe.copy()
                plt.subplot(2, 2, subplotCounter)
                subplotCounter += 1
                for element in order[i]:
                    plotDF = df.groupby(xval[i])[scope].sum().reset_index()
                    plotDF[column2drop[i]] = element
                    sns.barplot(data=plotDF, x=xval[i], y=scope, hue=column2drop[i], palette=palette[i])
                    df.drop(df[df[column2drop[i]] == element].index, inplace=True)
                plt.legend()
        plt.show()

    def stackedBarchartsMatplotlib(self, xval):

        df = self.dfObj.countDataframe

        if xval == "Category":
            order1 = self.statusOrder.keys()
            filterEntry1 = "Status"
            order2 = self.categoryOrder.keys()
            filterEntry2 = "Category"

        elif xval == "Status":
            order1 = self.categoryOrder.keys()
            filterEntry1 = "Category"
            order2 = self.statusOrder.keys()
            filterEntry2 = "Status"


        for counter, element1 in enumerate(order1):
            filteredDF = df[df[filterEntry1] == element1]
            y = []
            for element2 in order2:
                y.append(list(filteredDF[filteredDF[filterEntry2] == element2]["Count"])[0])
            if counter == 0:
                plt.bar(order2, y, label=element1)
                ybottom = y
            else:
                plt.bar(order2, y, bottom=ybottom, label=element1)
                ybottom = np.add(ybottom, y)
        plt.legend()
        plt.show()

    def sideBySideBarchart(self):

        df = self.dfObj.countDataframe

        t = len(df["Status"].unique())
        d = len(df["Category"].unique())
        w = 0.8

        for n, status in zip(range(1, t+1), self.statusOrder.keys()):
            filteredDF = df[df["Status"] == status]
            y = []
            for category in self.categoryOrder.keys():
                y.append(list(filteredDF[filteredDF["Category"] == category]["Count"])[0])
            x = [t * element + w * n for element in range(d)]
            ax = plt.subplot()
            plt.bar(x, y, label=status)

            if t % 2 == 0:
                if n == t/2:
                    xticks = x
                elif n == (t/2) + 1:
                    xticks = np.add(xticks, x)
                    xticks = xticks/2

                    ax.set_xticks(xticks)
                    ax.set_xticklabels(self.categoryOrder.keys())

        plt.legend()
        plt.show()

    def pieCharts(self):

        df = self.dfObj.countDataframe
        for counter, status in enumerate(self.statusOrder.keys()):
            filteredDF = df[df["Status"] == status]
            y = []
            for category in self.categoryOrder.keys():
                y.append(list(filteredDF[filteredDF["Category"] == category]["Count"])[0])

            plt.subplot(2, 2, counter+1)

            plt.pie(y, autopct="%0.2f%%")
            plt.legend(self.categoryOrder.keys())
            plt.title(status)
            plt.axis("equal")
        plt.show()

    def correlationPlot(self):

        df = self.dfObj.countDataframe

        df["Status"] = pd.Categorical(df["Status"], self.statusOrder.keys(), ordered=True)
        df["Status"] = df["Status"].cat.codes

        # find the 75% quantile for each "Status" and consider the maximum
        lst = []
        for status in df["Status"].unique():
            lst.append(np.quantile(df[df["Status"] == status]["Count"], 0.75))
        maxQuantile = np.amax(lst)

        ax = plt.subplot()
        sns.regplot(data=df, x="Status", y="Count", scatter_kws={'alpha':0.3})
        plt.axis([-1, 4, 0, maxQuantile])

        ax.set_xticks(sorted(list(df["Status"].unique())))
        ax.set_xticklabels(self.statusOrder.keys())

        plt.show()



if __name__ == '__main__':

    dataframe = dataFrameClass(path, fileName1, fileName2)
    speciesPlot = PlotClass(dataframe)








    a = 1

