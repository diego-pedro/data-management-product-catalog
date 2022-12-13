Feature: Build shopping cart

  Scenario Outline: Add products to his cart
   Given access to the system with <username> and <password>
   When they search for a <existing> product with <stock>
   Then receives <response_status>

    Examples:
      |     username      | password   | existing | stock |  response_status  |
      | test@email.com.br | Test#1234  |   True   |   1   |         200       |
      | test@email.com.br | Test#1234  |   False  |   1   |         406       |
      | test@email.com.br | xTest#1234 |   True   |   1   |         401       |
      | test@email.com.br | Test#1234  |   True   |   0   |         406       |


  Scenario Outline: Remove products from his cart
   Given access to the system with <username> and <password>
   When they search for a <existing> product in his cart
   Then receives <response_status>

    Examples:
      |     username      | password   | existing | response_status |
      | test@email.com.br | Test#1234  |   True   |       200       |
      | test@email.com.br | Test#1234  |   False  |       406       |
      | test@email.com.br | xTest#1234 |   True   |       401       |