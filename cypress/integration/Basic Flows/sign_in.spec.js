/// <reference types="cypress" />

context('Signing in', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8000/login')
  })

  it('can enter login credentials', () => {
    let blueprintUser = {
      'name': 'admin',
      'password': 'thVHc4uusAEB'
    }

    // logging in
    cy.get('#sign-in-toggle').click()
    cy.get('#id_login').type(blueprintUser.name)
    cy.get('#id_password').type(blueprintUser.password)
    cy.get('#sign-in-submit').click()

    cy.get('#user-menu-dropdown').should('contains.text', blueprintUser.name)

    // signing out
    cy.get('#user-menu-dropdown').click()
    cy.get('#nav-logout-btn').click()
    cy.get('.usa-alert__body').should('contains.text', 'You have signed out.')    
  })
})