/// <reference types="cypress" />

context('Component Library', () => {
  before(()=> {
    cy.loginWithUI()

    //make sure that there is a project to work with when only running this file
    let projectTitle = "Componenet Library Test"
    let projectAcronym = "CLT"

    cy.visit(Cypress.env('baseUrl') + '/packages/create')

    // filling out form
    cy.get('#id_title').type(projectTitle)
    cy.get('#id_acronym').type(projectAcronym)
    cy.get('.usa-radio__label').contains('CMS AWS Commercial East-West').click()

    cy.get('.usa-radio__label').contains('Low').click()
    cy.get('#next-button').click()
  })
  
  it('user can view component library page', () => {
    cy.visit(Cypress.env('baseUrl') + '/controls/components')
    cy.get('a').contains('Active Directory').click()

    cy.get('.usa-accordion__button').contains('CMS Implementation Standard').click()
    cy.get('#b-a1').should('be.visible')

    cy.get('.usa-accordion__button').contains('Guidance').click()
    cy.get('#b-a2').should('be.visible')

    // always visibile on page load
    cy.get('#b-a3').should('be.visible')
  })
})