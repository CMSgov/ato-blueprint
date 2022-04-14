/// <reference types="cypress" />

context('Signing in', () => {
  beforeEach(() => {
    cy.visit(Cypress.env('loginUrl'))
  })

  it('can enter login credentials through UI', () => {
    // start a clean session
    cy.clearCookies
    cy.clearLocalStorage

    // logging in
    cy.get('#sign-in-toggle').click()
    cy.get('#id_login').type(Cypress.env('dev_user').name)
    cy.get('#id_password').type(Cypress.env('dev_user').password)
    cy.get('#sign-in-submit').click()

    cy.get('#user-menu-dropdown').should('contains.text', Cypress.env('dev_user').name)

    // signing out
    cy.get('#user-menu-dropdown').click()
    cy.get('#nav-logout-btn').click()
    cy.get('.usa-alert__body').should('contains.text', 'You have signed out.')    
  })

  // this example can be used in before actions of other files
  it('csrf token can be used to login without UI', () => {
    cy.request(Cypress.env('loginUrl'))
      .its('body')
      .then((body) => {
        const $html = Cypress.$(body)
        const csrf  = $html.find("input[name=csrfmiddlewaretoken]").val()

        cy.devLoginByCSRF(csrf)
          .then((resp) => {
            expect(resp.status).to.eq(200)
          })
      })
  })
})