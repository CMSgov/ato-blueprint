/// <reference types="cypress" />

context('Projects', () => {
  beforeEach(() => {
    cy.loginWithUI()
  })

  it('user can create a new project', () => {
    let projectTitle = "Fake Title"
    let projectAcronym = "FT"

    cy.visit(Cypress.env('baseUrl') + '/packages/create')

    // filling out form
    cy.get('#id_title').type(projectTitle)
    cy.get('#id_acronym').type(projectAcronym)
    cy.get('.usa-radio__label').contains('CMS AWS Commercial East-West').click()

    cy.get('.usa-radio__label').contains('Low').click()
    cy.get('#next-button').click()

    //in the future this will automatically redirect to the correct page
    // this is a stand in until we update routing
    cy.visit(Cypress.env('baseUrl') + '/packages')
    cy.get('.usa-card__heading').should('contains.text', projectTitle)
    cy.get('.usa-card__heading').should('contains.text', projectAcronym)

  })

  it('user can view project details', () => {
    let projectTitle = "Fake Title"

    cy.visit(Cypress.env('baseUrl') + '/packages')
    cy.get('.usa-card').contains(projectTitle).get('a').contains('Manage Components').click()

    // assert important navigation buttons are present
    cy.get('#project-controls').should('contain.text', 'Review Controls')
    cy.get('#project-components').should('contain.text', 'Manage Components')
    cy.get('#project-ssp').should('contain.text', 'Export System Security Plan')
  })
})