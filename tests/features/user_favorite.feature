Feature: User can add new favorite category for desired products

  Scenario: User searches for a desired product
   Given the user wishes to buy a specific product
   When the catalogue service displays the associated search results
   Then the user views the desired product's details

  Scenario: User adds new favorite category
   Given the user wants to be notified when new products of a favorite category arrive
   When the user views a product that belongs to a desired category and add that category to his list
   Then the user is notified when a new product of that category is added