Feature: Checkout

  Scenario Outline: Checkout user cart
    Given resolve <address>
    When resolve payment <p_status>
    Then resolve delivery <receipt>

    Examples:
      |       address        | p_status |  receipt |
      |  Rua Aurelio's, 122  |   True   |   True   |
      |         None         |   True   |   False  |
      |         None         |   False  |   False  |
      |  Rua Gabriel, 71     |   False  |   False  |
