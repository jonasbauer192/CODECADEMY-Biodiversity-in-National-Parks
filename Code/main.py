from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np
from scipy.stats import chi2_contingency

path = "D:\CODECADEMY-Biodiversity-in-National-Parks"
fileName1 = "observations.csv"
fileName2 = "species_info.csv"

class DataframeClass:

    def __init__(self, path, fileName1, fileName2):
        self.path = path
        self.fileName1 = fileName1
        self.fileName2 = fileName2
        self.createDataframe()
        self.chiSquareDataframe()
        self.cleanDataframe()
        self.categoryDataframe = self.countDataframe("Category")
        self.parkDataframe = self.countDataframe("Park")
        self.proportionsDataframe()
        self.overviewDataframe()

    def createDataframe(self):
        os.chdir(path)
        df1 = pd.read_csv(self.fileName1)
        df2 = pd.read_csv(self.fileName2)
        self.dataframe = pd.merge(df1, df2)

    def chiSquareDataframe(self):

        df = self.dataframe[["scientific_name", "category", "conservation_status"]]
        df.columns = ["Name", "Category", "Status"]

        df = df.fillna(value={"Status": "Safe"})
        for status in df["Status"].unique():
            if not status == "Safe":
                df["Status"] = df["Status"].replace(status, "Not Safe", regex=True)

        self.chiSquareDataframe = df

    def cleanDataframe(self):
        self.dataframe = self.dataframe.drop_duplicates(subset=["common_names"])
        self.dataframe = self.dataframe.dropna()
        self.dataframe = self.dataframe.drop(columns=["scientific_name", "common_names"])
        self.dataframe.columns = ["Park", "Observations", "Category", "Status"]
        self.dataframe["Count"] = 1

    def countDataframe(self, objective):
        df1 = self.dataframe.groupby(objective)["Observations"].sum().reset_index()

        df2 = self.dataframe.groupby([objective, "Status"])["Count"].sum().reset_index()
        for element in df2[objective].unique():
            filteredDf = df2[df2[objective] == element]
            # if the df does not contain a row for a status entry create it and set its count to 0
            for status in self.dataframe["Status"].unique():
                if not status in filteredDf["Status"].unique():
                    df2 = df2.append(
                        {objective: element, "Status": status, "Count": 0}, ignore_index=True)

        df = pd.merge(df1, df2)
        df = df.sort_values(by=[objective, "Status"])
        return df

    def proportionsDataframe(self):
        proportion = lambda row: (row["Count"] / row["Observations"]) * 100
        self.categoryDataframe["Proportion"] = self.categoryDataframe.apply(proportion, axis=1)
        self.categoryDataframe.drop(columns=["Observations"])

    def overviewDataframe(self):

        for objective in ["Count", "Proportion"]:
            df = self.categoryDataframe.pivot(
                index="Category",
                columns="Status",
                values=objective).reset_index()
            df.to_csv(f"{objective} of Status per Category.csv")

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
        self.pieCharts("Category")
        self.pieCharts("Park")
        self.correlationPlot()

    def stackedBarcharts(self):
        objectives = ["Count", "Proportion"]
        xval = ["Status", "Category"]
        column2drop = ["Category", "Status"]
        palette = [self.categoryOrder, self.statusOrder]

        plt.figure("Stacked Bar Charts", figsize=(16,9))
        subplotCounter = 1
        for objective in objectives:
            # loop to create a single subplot
            for i in range(len(xval)):
                df = self.dfObj.categoryDataframe.copy()
                plt.subplot(2, 2, subplotCounter)
                subplotCounter += 1
                for element in df[column2drop[i]].unique():
                    plotDF = df.groupby(xval[i])[objective].sum().reset_index()
                    plotDF[column2drop[i]] = element
                    sns.barplot(data=plotDF, x=xval[i], y=objective, hue=column2drop[i], palette=palette[i])
                    df.drop(df[df[column2drop[i]] == element].index, inplace=True)
                plt.legend()
        plt.savefig("Stacked Bar Charts.png")

    def pieCharts(self, objective):
        if objective == "Category":
            df = self.dfObj.categoryDataframe
            filterColumn = "Status"
            legend = "Category"
        elif objective == "Park":
            df = self.dfObj.parkDataframe
            filterColumn = "Park"
            legend = "Status"

        plt.figure("Pie Charts (" + objective + ")", figsize=(16,9))
        for counter, element in enumerate(df[filterColumn].unique()):
            filteredDF = df[df[filterColumn] == element]

            plt.subplot(2, 2, counter+1)

            plt.pie(filteredDF["Count"], autopct="%0.2f%%")
            plt.legend(filteredDF[legend])
            plt.title(element)
            plt.axis("equal")
        plt.savefig("Pie Charts " + objective + ".png")

    def correlationPlot(self):
        df = self.dfObj.categoryDataframe

        df["Status"] = pd.Categorical(df["Status"], self.statusOrder.keys(), ordered=True)
        df["Status"] = df["Status"].cat.codes

        plt.figure("Correlation Plot", figsize=(16, 9))
        # find the 75% quantile for each "Status" and consider the maximum
        lst = []
        for status in df["Status"].unique():
            lst.append(np.quantile(df[df["Status"] == status]["Count"], 0.75))
        maxQuantile = np.amax(lst)

        ax = plt.subplot()
        sns.regplot(data=df, x="Status", y="Count", scatter_kws={'alpha': 0.3})
        plt.axis([np.amin(df["Status"]) - 1, np.amax(df["Status"]) + 1, 0, maxQuantile])

        ax.set_xticks(sorted(list(df["Status"].unique())))
        ax.set_xticklabels(self.statusOrder.keys())

        plt.savefig("Correlation Plot.png")

class HypothesisTestingClass:
    def __init__(self, dataframe):
        self.df = dataframe.chiSquareDataframe
        self.chiSquareTest()

    def chiSquareTest(self):
        crossTab = pd.crosstab(self.df["Category"], self.df["Status"])
        chi2, pval, dof, expected = chi2_contingency(crossTab)

if __name__ == '__main__':

    dataframe = DataframeClass(path, fileName1, fileName2)
    speciesPlot = PlotClass(dataframe)
    chiSquareTest = HypothesisTestingClass(dataframe)
