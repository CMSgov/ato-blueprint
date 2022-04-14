// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

Cypress.Commands.add('loginWithUI', () => {
  cy.visit(Cypress.env('loginUrl'))
  cy.get('#sign-in-toggle').click()
  cy.get('#id_login').type(Cypress.env('dev_user').name)
  cy.get('#id_password').type(Cypress.env('dev_user').password)
  cy.get('#sign-in-submit').click()

  cy.get('#user-menu-dropdown').should('contains.text', Cypress.env('dev_user').name)
})

Cypress.Commands.add('devLoginByCSRF', (csrfToken) => {
  cy.request({
    method: 'POST',
    url: Cypress.env('loginUrl'),
    failOnStatusCode: false,
    form: true,
    followRedirect: true,
    headers: {
      Referer: Cypress.env('loginUrl')
    },
    body: {
      username: Cypress.env('dev_user').name,
      password: Cypress.env('dev_user').password,
      csrfmiddlewaretoken: csrfToken
    }
  })
})