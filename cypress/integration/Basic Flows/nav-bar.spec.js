/// <reference types="cypress" />

const { get } = require("lodash")

context('Navigation', () => {
    beforeEach(() => {
        cy.loginWithUI()
    })

    it('properly renders the navigation', () => {
        cy.get('.navbar').should('be.visible')
        cy.get('.navbar').should('contain.text', 'Projects')
        cy.get('.navbar').should('contain.text', 'Component Library')
    })
})