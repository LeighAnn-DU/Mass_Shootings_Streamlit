
import matplotlib.pyplot    as plt
import numpy                as np
import pandas               as pd
import plotly.express       as px
import plotly.graph_objects as go
import seaborn              as sns
import streamlit            as st

from plotly.subplots        import make_subplots

MSData = pd.read_csv("FinalMS.csv")
MSData["City"] = MSData["City"].str.strip()
#MSData["Date"] = pd.to_datetime(MSData["Date"], origin='1960-01-01')
MSData["Year"] = pd.DatetimeIndex(MSData["Date"]).year
MSData["AutoWeapon"]=np.where(MSData["AutoWeapon"].isnull(), None,
                    np.where(MSData["AutoWeapon"]==1, "Automatic/Semi-Automatic", 
                    "Other Type of Gun"))
yearsby5 = np.arange(1966, 2021+1,5)
YearLabels=[f'{yearsby5[i]}-{yearsby5[i+1]-1}' for i in range(len(yearsby5)-1)]+["2021-2025"]
MSData["YearCat"] = pd.cut(MSData["Year"], bins = np.insert(yearsby5, 12, 2025), labels=YearLabels, right=False)
MSData["YearCat"]=MSData["YearCat"].cat.reorder_categories(YearLabels)

#Data Frame in Global Environment
DayLabels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MSData["Day of Week"]=pd.Categorical(MSData["Day of Week"], ordered=True, categories=DayLabels)
SeasonLabels = ["Spring", "Summer", "Fall", "Winter"]
MSData["Season"]=pd.Categorical(MSData["Season"], ordered=True, categories=SeasonLabels)
GenderCounts = MSData["Male"].value_counts().reset_index()
GenderCounts.columns=["Male", "Number of Shootings"]
AgeLabels2 = ["Middle School", "High School", "College Age", "20s", "30s", "40s", "50s", "Older than 60", "Multiple Shooters"]
SACCounts = MSData["Shooter Age Category"].value_counts().reset_index()
SACCounts.columns=["Shooter Age Category", "Number of Shootings"]
SACCounts["Shooter Age Category"]=pd.Categorical(SACCounts["Shooter Age Category"], ordered=True, categories=AgeLabels2)
RaceLabels = ["Asian", "Black", "Latino", "Native American", "Other", "White"]
RaceCounts = MSData["Race/Ethnicity"].value_counts().reset_index()
RaceCounts.columns=["Race/Ethnicity", "Number of Shootings"]
RaceCounts["Race/Ethnicity"]=pd.Categorical(RaceCounts["Race/Ethnicity"], ordered=True, categories=RaceLabels)
MHCounts = MSData["Prior Mental Illness"].value_counts().reset_index()
MHCounts.columns=["Prior Mental Illness", "Number of Shootings"]
AgeLabels = ["Middle School", "High School", "College Age", "20s", "30s", "40s", "Older than 60", "Multiple Shooters"]
SchMH = MSData.loc[(MSData["School"]==1) & (MSData["Prior Mental Illness"]!="Unknown"), 
                   ["Fatalities", "Injured", "Prior Mental Illness", "Shooter Age Category", "State", "YearCat"]].copy()
SchMH["Shooter Age Category"]=pd.Categorical(SchMH["Shooter Age Category"], ordered=True, categories=AgeLabels)

#Plotly Graph Data Frames (includes adding fake data to make legends work)
CensusRegions = pd.read_csv("https://raw.githubusercontent.com/cphalpert/census-regions/master/us%20census%20bureau%20regions%20and%20divisions.csv")

CensusRegions=CensusRegions[["State Code","Division"]]
CensusRegions.rename({"State Code": "State"}, axis=1, inplace=True)
StateYearAge = MSData.loc[(~MSData["Shooter Age"].isnull()) & (MSData["Shooter Age"]<100)].copy()
StateYearAge = StateYearAge.groupby(["YearCat", "State"]).aggregate({"Fatalities": ["sum", "count", "mean"], 
                                                         "Injured": ["sum", "mean"],
                                                        "Shooter Age": ["mean"]})
StateYearAge.columns=["_".join(i) for i in StateYearAge.columns.to_flat_index()]
StateYearAge.rename({"Fatalities_count": "Shootings_Count"}, axis=1, inplace=True)
StateYearAge.reset_index(inplace = True)
StateYearAge = pd.merge(StateYearAge, CensusRegions, how="left", on=["State"])

#adding five pieces of fake data to get graph to work
StateYearAge.loc[(StateYearAge["YearCat"]=='1966-1970') & (StateYearAge["State"]=="AK"), 
                 ["Fatalities_sum", "Shootings_Count"]]=0.001,0.001
StateYearAge.loc[(StateYearAge["YearCat"]=='1966-1970') & (StateYearAge["State"]=="AL"), 
                 ["Fatalities_sum", "Shootings_Count"]]=0.001,0.001
StateYearAge.loc[(StateYearAge["YearCat"]=='1966-1970') & (StateYearAge["State"]=="CT"), 
                 ["Fatalities_sum", "Shootings_Count"]]=0.001,0.001
StateYearAge.loc[(StateYearAge["YearCat"]=='1966-1970') & (StateYearAge["State"]=="DC"), 
                 ["Fatalities_sum", "Shootings_Count"]]=0.001,0.001
StateYearAge.loc[(StateYearAge["YearCat"]=='1966-1970') & (StateYearAge["State"]=="IA"), 
                 ["Fatalities_sum", "Shootings_Count"]]=0.001,0.001
autoCols=["Fatalities", "AutoWeapon", "Shooter Age", "YearCat", "State"]
shooterAgedf= MSData.loc[MSData["Shooter Age"]<100, 
                         autoCols].dropna().sort_values("YearCat").reset_index(drop=True)
shooterAgedf.loc[len(shooterAgedf.index)]=[-1, "Automatic/Semi-Automatic", 0, 
                                           "1966-1970", "ND"]
# City Latitude/Longitude Data Frames                                                                                    
CityData = MSData.groupby(["City", "State"])[["Fatalities", "Injured"]].sum().reset_index()
CityLonLat = pd.merge(MSData.loc[~MSData.duplicated(["City", "State"]), ["City", "State", "Latitude", "Longitude"]],
                      CityData, on=["City", "State"])
CityHoverText = [f'{CityLonLat["City"].values[i]}  \nFatalities: {CityLonLat["Fatalities"].values[i]}  \nInjured: {CityLonLat["Injured"].values[i]}' for i in range(CityLonLat.shape[0])]

st.title("Mass Shootings From 1966 to Spring 2021")
st.text("")
st.text("")
st.header("Data for this project was gathered from the following resources:")
st.subheader("The Violence Project:  https://www.theviolenceproject.org/mass-shooter-database/")
st.subheader("The Gun Violence Archive:  https://www.gunviolencearchive.org")
st.subheader("Mother Jones:  https://www.motherjones.com/politics/2012/12/mass-shootings-mother-jones-full-data/")
st.subheader("The Stanford Mass Shootings in America Database, courtesy of the Stanford Geospatial Center and Stanford Libraries:  https://github.com/StanfordGeospatialCenter/MSA/tree/master/Data")
st.text("")
st.subheader("After merging the data from these four databases and removing duplicates, the database used for this project contains just over 3000 datapoints (shootings).  Incidentally, there are no mass shootings from North Dakota in this database, primarily because of the definition above.")
st.text("")
st.header("Definition of Mass Shooting")
st.subheader("There is no universally accepted definition of a mass shooting. The Congressional Research Service definition, which is quite conservative is:  'a multiple homicide incident in which four or more victims are murdered with firearms—not including the offender(s)—withinone event, and at least some of the murders occurred in a public location or locations inclose geographical proximity (e.g., a workplace, school, restaurant, or other public settings), and the murders are not attributable to any other underlying criminal activity or commonplace circumstance (armed robbery, criminal competition, insurance fraud, argument, or romantic triangle).'")
st.text("")
st.text("")
st.header("Exploratory Data Analysis")
st.text("")
st.subheader("Shootings and Fatalities by Day of the Week")
st.markdown("There are more shootings on weekend days, but Wednesday appears to be the most fatal!")
#DOW Day of Week
def DOWBarChart():
    DOWCounts = MSData["Day of Week"].value_counts().reset_index()
    DOWCounts.columns=["Day of Week", "Number of Shootings"]
    DOWCounts["Day of Week"]=pd.Categorical(DOWCounts["Day of Week"], ordered=True, categories=DayLabels)

    fig,ax=plt.subplots(1,2, figsize=(20,8), sharey=True, sharex=False)

    ax.flat[0].set_title("Fatalities by Day of the Week")
    sns.boxplot(ax=ax.flatten()[0], x="Fatalities", y="Day of Week", data=MSData, orient="h")
    ax.flat[0].set_xlabel("Fatalities")
    ax.flat[0].set_ylabel("Day of Week")

    ax.flat[1].set_title("Number of Shootings per Day of Week")
    sns.barplot(ax=ax.flatten()[1], x="Number of Shootings", y="Day of Week", data=DOWCounts, orient="h")
    ax.flat[1].set_xlabel("Number of Shootings")
    ax.flat[1].set_ylabel("")
    return fig
st.pyplot(DOWBarChart())

st.subheader("Shootings and Fatalities by Season")
st.markdown("Summer has more shootings, but winter has more deaths.")

#Season
def SeasonGraphs():
    SeasonLabels = ["Spring", "Summer", "Fall", "Winter"]
    SeasCounts = MSData["Season"].value_counts().reset_index()
    SeasCounts.columns=["Season", "Number of Shootings"]
    SeasCounts["Season"]=pd.Categorical(SeasCounts["Season"], ordered=True, categories=SeasonLabels)

    fig,ax=plt.subplots(1,2, figsize=(20,8), sharey=True, sharex=False)
    ax.flat[0].set_title("Fatalities by Season")
    sns.boxplot(ax=ax.flatten()[0], x="Fatalities", y="Season", data=MSData, orient="h")
    ax.flat[0].set_xlabel("Fatalities")
    ax.flat[0].set_ylabel("Season")

    ax.flat[1].set_title("Number of Shootings per Season")
    sns.barplot(ax=ax.flatten()[1], x="Number of Shootings", y="Season", data=SeasCounts, orient="h")
    ax.flat[1].set_xlabel("Number of Shootings")
    ax.flat[1].set_ylabel("")
    return fig
st.pyplot(SeasonGraphs())

st.subheader("Shootings by Gender, Prior Mental Illness, Race/Ethnicity, and Shooter Age")
st.markdown("Because of the large number of male shooters, the dependent axis is set pretty high for all four graphs.")

# Gender, Shooter Age, Race/Ethnicity, Prior Mental Illness
def demographicBarCharts():
    fig,ax=plt.subplots(2,2, figsize=(20,16), sharey=True, sharex=False)

    ax.flat[0].set_title("Number of Shootings by Gender")
    sns.barplot(ax=ax.flatten()[0], x="Male", y="Number of Shootings", data=GenderCounts, orient="v")
    ax.flat[0].set_xlabel("Gender")
    ax.flat[0].set_ylabel("Number of Shootings")

    ax.flat[1].set_title("Number of Shootings by Prior Mental Illness")
    sns.barplot(ax=ax.flatten()[1], x="Prior Mental Illness", y="Number of Shootings", 
            data=MHCounts.loc[MHCounts["Prior Mental Illness"]!="Unknown"], orient="v")
    ax.flat[1].set_ylabel("")

    ax.flat[2].set_title("Number of Shootings by Shooter Race/Ethnicity")
    sns.barplot(ax=ax.flatten()[2], x="Race/Ethnicity", y="Number of Shootings", data=RaceCounts, orient="v")
    ax.flat[2].set_xticklabels(RaceLabels, rotation=60)
    ax.flat[2].set_ylabel("Number of Shootings")

    ax.flat[3].set_title("Number of Shootings by Shooter Age")
    sns.barplot(ax=ax.flatten()[3], x="Shooter Age Category", y="Number of Shootings", data=SACCounts, orient="v")
    ax.flat[3].set_xticklabels(AgeLabels2, rotation=60)
    ax.flat[3].set_ylabel("")
    fig.tight_layout()
    return fig
st.pyplot(demographicBarCharts())

st.subheader("Shooters with Prior Mental Illness (or not) and Resulting Fatalities or Injuries")

#Prior Mental Illness with Fatalities and Injuries
def MHFatInj():
    fig,ax=plt.subplots(1,2, figsize=(20,8), sharey=True, sharex=False)

    ax.flat[0].set_title("Fatalities by Prior Mental Illness")
    sns.boxplot(ax=ax.flatten()[0], x="Fatalities", y="Prior Mental Illness", data=SchMH, orient="h")
    ax.flat[0].set_xlabel("Fatalities")
    ax.flat[0].set_ylabel("Prior Mental Illness")

    ax.flat[1].set_title("Injuries by Prior Mental Illness")
    sns.barplot(ax=ax.flatten()[1], x="Injured", y="Prior Mental Illness", data=SchMH, orient="h")
    ax.flat[1].set_xlabel("Number of Injuries")
    ax.flat[1].set_ylabel("")
    return fig
st.pyplot(MHFatInj())

st.subheader("Shooter Age, Fatalities, Use of Automatic/Semi-Automatic Weapons or Prior Mental Illness")
st.markdown("As the US considers what to do about mass shootings and gun violence, these two factors (automatic weapons and mental health issues) are frequently brought into the conversation.  Automatic weapons were banned in 1994, and the law expired in 2004.")

## Shooter Age with AutoWeapon and Mental Illness
def AgeFatalScatter():
    fig,ax=plt.subplots(1,2, figsize=(20,8), sharey=True, sharex=False)

    ax.flat[0].set_title("Shooter's Age with Automatic Weapon with Fatalities")
    sns.scatterplot(ax=ax.flatten()[0], x="Shooter Age", y="Fatalities", 
            data=MSData.loc[MSData["Shooter Age"]<100], hue="AutoWeapon")
    ax.flat[0].set_xlabel("Shooter Age")
    ax.flat[0].set_ylabel("Fatalities")

    ax.flat[1].set_title("Shooter's Age and Fatalities with Prior Mental Illness")
    sns.scatterplot(ax=ax.flatten()[1], x="Shooter Age", y="Fatalities", hue="Prior Mental Illness",
            data=MSData.loc[(MSData["Shooter Age"]<100) & (MSData["Prior Mental Illness"]!="Unknown")])
    ax.flat[1].set_xlabel("Shooter Age")
    ax.flat[1].set_ylabel("")
    return fig
st.pyplot(AgeFatalScatter())
st.text("")
st.header("Interactive Graphs to Show Connections")
st.text("")
st.subheader("Mass Shootings of the Last 55 Years")
st.markdown("Push button to activate timeline.  The timeline can be stopped at each 5-Year Interval. Hover over each dot to see state, region, number of shootings, and fatalities.  Dot size represents total fatalities.")

#Mass Shootings over 55 Years
MSYears = px.scatter(StateYearAge, x="Shootings_Count", y="Fatalities_sum",  color="Division",
           hover_name="State", animation_frame="YearCat", size="Fatalities_sum", size_max=55,
           animation_group="State", range_x=[0,10], range_y=[0,70], 
           title="Mass Shootings of the Last 55 Years",
           labels=dict(YearCat="Years",Fatalities_sum="Number of Fatalities", 
                       Shootings_Count="Number of Shootings"))
st.plotly_chart(MSYears)  

st.text("")
st.subheader("Mass Shootings and Fatalities by Weapon of the Last 55 Years")
st.markdown("Push button to activate timeline.  The timeline can be stopped at each 5-Year Interval.  Hover over each dot to see state, shooter age, and number of fatalities.")

#Shootings by Weapon Type
WeaponShoot = px.scatter(shooterAgedf, x="Shooter Age", y="Fatalities",  
           color="AutoWeapon", hover_name="State", animation_frame="YearCat", 
           animation_group="State", range_x=[10,70], range_y=[0,70], 
           title="Mass Shootings/Fatalities by Weapon Type of the Last 55 Years",
           labels=dict(YearCat="Years", Fatalities="Number of Fatalities"))
st.plotly_chart(WeaponShoot)
st.text("")
st.subheader("School Shootings")
st.markdown("As an educator, school shootings are quite impactful and frightening.  This graph illustrates shooter age by category, prior mental health, and the resulting fatalities.  Hover over each box plot to see the 5-Number Summary.  A horizonal bar with no box represents one shooting.  Note:  College-aged shooters have evidence of prior mental health issues.")

#School Shootings with Prior Mental Health
SCHMHShoot=px.box(SchMH, x="Prior Mental Illness", y="Fatalities", category_orders={"Shooter Age Category": AgeLabels},
            color = "Shooter Age Category", hover_name="Shooter Age Category",  
           title="School Shooting Fatalities with Prior Mental Illness",
           labels=dict(YearCat="Years", Fatalities="Number of Fatalities"))
st.plotly_chart(SCHMHShoot)

st.text("")
st.subheader("Fatalities Ratio by Region and State")
st.markdown("Hover over each state to see the number of shootings and the ratio of fatalities per shooting.  Be sure to look for states with fewer shootings like Hawaii and Maine.")

#Fatalities Ratio by Region and State (Sunburst Graph)
df = MSData.copy()
df["Number of Shootings"]=1
df["Fatalities Ratio"]=df["Fatalities"]/df["Number of Shootings"]
FatRatio = px.sunburst(df, path=['Division', 'State'], values='Number of Shootings', branchvalues="total",
                   color = "Fatalities Ratio", color_continuous_scale='RdBu', hover_data=["State"],
                 title="Ratio of Fatalities to Shootings by Region and State")
st.plotly_chart(FatRatio)

st.text("")
st.header("Interactive Maps to Show Geographic Connections")
st.text("")
st.text("")
st.subheader("Shootings by State")
st.markdown("Hover over each state to see the number of mass shootings that have occurred in each state.  Note: The database has no mass shooting data for North Dakota because of the definition of mass shooting.")

#Shooting per State (Choropleth Map)
StateShoot = MSData["State"].value_counts().reset_index()
#shootings per state
ShSt = px.choropleth(StateShoot, locations=StateShoot["index"], locationmode="USA-states",
 color="State",color_continuous_scale="PRGn",
 range_color=(0, 100),scope="usa",labels={"State": "Number of Shootings"},hover_name="index",
 hover_data={"index":False,"State":True})
ShSt.update_layout(title={"text": "Number of Shootings by State", "xanchor": "left", "x": 0.5, 
                          "font_size": 16}, margin={"r":0,"t":75,"l":0,"b":0})
st.plotly_chart(ShSt)

st.text("")
st.subheader("Fatalities and Injuries by State")
st.markdown("Hover over each state to see the number of fatalities and injuries that resulted from shootings.")

# Fatalities and Injuries by State (Choropleth Map)
FatInj = MSData.groupby("State")[["Fatalities", "Injured"]].sum().reset_index()
#fatalities and injuries per state
FatInjMap = px.choropleth(FatInj, locations=FatInj["State"], locationmode="USA-states",
 color="Fatalities",color_continuous_scale="YlOrRd",
 range_color=(0, 100),scope="usa",labels={"Fatalities": "Number of Fatalities", "Injured": "Number of Injured"},
                     hover_name="State", hover_data={"State":False,"Fatalities":True, "Injured": True})
FatInjMap.update_layout(title={"text": "Fatalities and Injuries per State", "xanchor": "left", "x": 0.5,
                          "font_size": 16}, margin={"r":0,"t":75,"l":0,"b":0}, 
                          hoverlabel=dict(bgcolor="#e6e6e6", font_size=12, font_family="Rockwell"))
st.plotly_chart(FatInjMap)

st.text("")
st.subheader("Fatalities and Injuries by State and City")
st.markdown("Hover over each gray bubble to see individual cities and the fatalities/injuries that have resulted from shootings in that city.  The number of shootings per state is also included. Be sure to check out the smaller cities behind the larger bubbles. Clearly Chicago has a large number of mass shootings!")

#fatalities and injuries per state and city
CityFatInj = px.choropleth(FatInj, locations=FatInj["State"], locationmode="USA-states",
 color="Fatalities",color_continuous_scale="Tealrose",
 range_color=(0, 100),scope="usa", labels={"Fatalities": "Number of Fatalities", "Injured": "Number of Injured"})

CityFatInj.add_trace(go.Scattergeo(
    locationmode = 'USA-states',
    lon = CityLonLat['Longitude'],
    lat = CityLonLat['Latitude'],
    hoverinfo = 'text',
    hovertext = CityHoverText,
    mode = 'markers',
    marker = dict(
        size = CityLonLat["Fatalities"], 
        color = 'rgb(102,102,102)',
        line = dict(
            width = 3,
            color = 'rgba(68, 68, 68, 0)'
        )
    )))
CityFatInj.update_layout(title={"text": "Fatalities and Injuries by City (No Data for North Dakota)", "xanchor": "left", "x": 0.,
                          "font_size": 16}, margin={"r":0,"t":75,"l":0,"b":0}, 
                          hoverlabel=dict(bgcolor="#e6e6e6", font_size=12, font_family="Rockwell"))
st.plotly_chart(CityFatInj)

st.text("")
st.header("Conclusion")
st.subheader("This project was the result of a discussion about current mass shootings and some questions:")
st.markdown("Are there more mass shootings now or is the press making us more aware of them now?")
st.markdown("Is there an increase of mass shootings as the US recovers from the pandemic?  OR")
st.markdown("Were there fewer mass shootings during the pandemic?")
st.markdown("Are there more mass shootings during the Biden presidency compared to the Trump presidency?")
st.markdown("How do gun laws of different states impact mass shootings?")
st.markdown("What can we do to improve support for those with mental health issues at an early age?")
st.markdown("What can the US do to curb mass shootings?  What factors need to be considered?")

