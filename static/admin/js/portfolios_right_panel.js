// On portgroup button click loading portgroup and portfolio data to port group editor modal
$("#PortGroupBtn").on("click", function (){

    // Fetching port group data from database
    let portGroups = getPortfolioData("Portfolio Group")

    // Fetching all portfolio data from database
    let portData = getPortfolioData("Portfolio")

    // Loading port group and portfolio data to adding section
    // loadDataToSelector("#addPortGroup", "portGroupOption", portGroups, "portData")
    // loadDataToSelector("#addPortSelect", "portOption", portData, "portData")

    // Loading port group data to removing section
    // loadDataToSelector("#removePortGroup", "portGroupOption", portGroups, "portData")

    // // Loading port group data to move section
    // loadDataToSelector("#movePortGroup", "portGroupOption", portGroups, "portData")
})

