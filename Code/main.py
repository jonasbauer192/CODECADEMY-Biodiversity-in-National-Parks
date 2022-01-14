from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np

path = "D:\CODECADEMY-Biodiversity-in-National-Parks"
fileName1 = "observations.csv"
fileName2 = "species_info.csv"

class dataFrameClass:
    """
    class to create, clean and modify dataframes
    """
    def __init__(self, path, fileName):
        self.path = path
        self.fileName = fileName
        self.dataframe = self.createDataframe()
        self.cleanDataframe()
        self.countStatusDataframe = self.countStatus()

    ### methods performed by initialization ###

    def createDataframe(self):
        os.chdir(path)
        return pd.read_csv(self.fileName)

    def cleanDataframe(self):
        self.dataframe = self.dataframe.drop_duplicates(subset=["common_names"])
        self.dataframe = self.dataframe.dropna()
        self.dataframe.columns = ["Category", "Name1", "Name2", "Status"]

    def countStatus(self):

        df = self.dataframe
        df["Count"] = 1
        df = self.dataframe.groupby(["Category", "Status"])["Count"].sum().reset_index()

        lst = []
        for category in df["Category"].unique():
            filteredDf = df[df["Category"] == category]

            # if the df does not contain a row for a status entry create it and set its count to 0
            for status in df["Status"].unique():
                if not status in filteredDf["Status"].unique():
                    df = df.append(
                        {"Category": category, "Status": status, "Count": 0}, ignore_index=True)

        return df


class speciesPlotClass:
    def __init__(self, dfObj):
        self.dfObj = dfObj
        self.statusOrder = ["In Recovery", "Species of Concern", "Threatened", "Endangered"]
        self.categoryOrder = ["Amphibian", "Bird", "Fish", "Mammal", "Nonvascular Plant", "Reptile", "Vascular Plant"]
        self.barCharts()
        self.pieCharts()
        self.correlationPlot()

    def barCharts(self):

        self.stackedBarcharts("Status")
        self.stackedBarcharts("Category")
        self.sideBySideBarchart()

    def sideBySideBarchart(self):

        df = self.dfObj.countStatusDataframe

        t = len(df["Status"].unique())
        d = len(df["Category"].unique())
        w = 0.8

        for n, status in zip(range(1, t+1), self.statusOrder):
            filteredDF = df[df["Status"] == status]
            y = []
            for category in self.categoryOrder:
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
                    ax.set_xticklabels(self.categoryOrder)

        plt.legend()
        plt.show()

    def stackedBarcharts(self, xval):

        df = self.dfObj.countStatusDataframe

        if xval == "Category":
            order1 = self.statusOrder
            filterEntry1 = "Status"
            order2 = self.categoryOrder
            filterEntry2 = "Category"

        elif xval == "Status":
            order1 = self.categoryOrder
            filterEntry1 = "Category"
            order2 = self.statusOrder
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

    def pieCharts(self):

        df = self.dfObj.countStatusDataframe
        for counter, status in enumerate(self.statusOrder):
            filteredDF = df[df["Status"] == status]
            y = []
            for category in self.categoryOrder:
                y.append(list(filteredDF[filteredDF["Category"] == category]["Count"])[0])

            plt.subplot(2,2,counter+1)

            plt.pie(y, autopct = "%0.2f%%")
            plt.legend(self.categoryOrder)
            plt.title(status)
            plt.axis("equal")
        plt.show()

    def correlationPlot(self):

        df = self.dfObj.countStatusDataframe

        df["Status"] = pd.Categorical(df["Status"], self.statusOrder, ordered=True)
        df["Status"] = df["Status"].cat.codes

        # find the 75% quantile for each "Status" and consider the maximum
        lst = []
        for status in df["Status"].unique():
            lst.append(np.quantile(df[df["Status"] == status]["Count"], 0.75))
        maxQuantile = np.amax(lst)

        ax = plt.subplot()
        sns.regplot(data=df, x="Status", y="Count")
        plt.axis([-1, 4, 0, maxQuantile])

        ax.set_xticks(sorted(list(df["Status"].unique())))
        ax.set_xticklabels(self.statusOrder)

        plt.show()

if __name__ == '__main__':

    #observations = dataFrameClass(path, fileName1)
    speciesDataframe = dataFrameClass(path, fileName2)
    speciesPlot = speciesPlotClass(speciesDataframe)




    a = 1

